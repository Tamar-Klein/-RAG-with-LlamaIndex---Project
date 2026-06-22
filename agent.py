import os
import json
import asyncio
from dotenv import load_dotenv
from netfree_unstrict_ssl import unstrict_ssl
import gradio as gr

from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere

# ייבוא הרכיבים של ה-Router וה-Workflow
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.tools import ToolMetadata
from llama_index.core.llms import ChatMessage

from llama_index.utils.workflow import draw_all_possible_flows
# ---------------------------------------------------------
# 1. הגדרת האירועים (Events)
# ---------------------------------------------------------
class RouteEvent(Event):
    """אירוע עבור נתב (Router) שיחליט לאן להמשיך"""
    query: str

class VectorSearchEvent(Event):
    """אירוע עבור נתיב החיפוש הסמנטי ב-Pinecone"""
    query: str

class StructuredSearchEvent(Event):
    """אירוע עבור נתיב שליפת הנתונים המובנים מה-JSON"""
    query: str

class SynthesizeEvent(Event):
    """אירוע אחרון: שילוב התשובות ושליחה ל-LLM"""
    query: str
    context: str
    source: str # שדה ששומר מאיפה הבאנו את המידע כדי להציג למשתמש

# ---------------------------------------------------------
# 2. ה-Workflow החכם שכולל Router
# ---------------------------------------------------------
class RoutingRAGWorkflow(Workflow):
    def __init__(self, pinecone_index, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retriever = pinecone_index.as_retriever(similarity_top_k=5)
        
        # בניית ה-Router (Selector)
        self.selector = LLMSingleSelector.from_defaults()
        
        # הגדרת "הכלים" כדי שה-Router ידע מתי לבחור כל אחד:
        self.choices = [
            ToolMetadata(
                name="vector_search",
                description="Useful for specific technical questions, finding how features work, definitions, semantic concepts or finding a specific color/guideline."
            ),
            ToolMetadata(
                name="structured_search",
                description="Useful for getting full lists, summaries, architecture decisions, open bugs, or rules across the entire project."
            )
        ]

    @step
    async def validate_input(self, ev: StartEvent) -> RouteEvent | StopEvent:
        """תחנה 1: ולידציה"""
        query = ev.get("query", "")
        if len(query.strip()) < 3:
            return StopEvent(result="אנא הכנס שאלה ברורה יותר.")
        
        print(f"\n✅ התקבל קלט: '{query}'")
        return RouteEvent(query=query)

    @step
    async def route_query(self, ev: RouteEvent) -> VectorSearchEvent | StructuredSearchEvent:
        """תחנה 2: הנתב (Router) בוחר את הנתיב הנכון"""
        print("🔀 מנתב את השאלה...")
        
        # ה-LLM בוחן את השאלה ואת הכלים ובוחר את הנתיב המתאים ביותר
        result = await self.selector.aselect(self.choices, query=ev.query)
        
        # תוקן: שולפים את האינדקס קודם ואז את השם
        selected_index = result.selections[0].index
        selected_tool = self.choices[selected_index].name        
        
        if selected_tool == "structured_search":
            print("🎯 החלטת הנתב: שליפה מובנית מקובץ JSON")
            return StructuredSearchEvent(query=ev.query)
        else:
            print("🧠 החלטת הנתב: חיפוש סמנטי מ-Pinecone")
            return VectorSearchEvent(query=ev.query)

    @step
    async def vector_search(self, ev: VectorSearchEvent) -> SynthesizeEvent | StopEvent:
        """תחנה 3א: חיפוש וקטורי"""
        print("🔍 מחפש ב-Pinecone...")
        nodes = await self.retriever.aretrieve(ev.query)
        if not nodes:
            return StopEvent(result="לא נמצא מידע רלוונטי בחיפוש הסמנטי.")
        
        # לוקח את כל הטקסטים ומאחד אותם למחרוזת אחת
        context_str = "\n\n".join([n.text for n in nodes])
        return SynthesizeEvent(query=ev.query, context=context_str, source="חיפוש סמנטי (Pinecone)")

    @step
    async def structured_search(self, ev: StructuredSearchEvent) -> SynthesizeEvent | StopEvent:
        """תחנה 3ב: שליפה מובנית מה-JSON"""
        print("📁 קורא נתונים מקובץ ה-JSON המובנה...")
        if not os.path.exists("extracted_data.json"):
            return StopEvent(result="שגיאה: קובץ extracted_data.json לא נמצא. אנא הרץ קודם את הסקריפט.")
            
        with open("extracted_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # ממיר את ה-JSON בחזרה לטקסט קריא עבור ה-LLM
        context_str = json.dumps(data, indent=2, ensure_ascii=False)
        return SynthesizeEvent(query=ev.query, context=context_str, source="נתונים מובנים (JSON)")

    @step
    async def synthesize(self, ev: SynthesizeEvent) -> StopEvent:
        """תחנה 4: ניסוח סופי עם ה-LLM"""
        print(f"✍️ מנסח תשובה (על בסיס: {ev.source})...")
        
        prompt = f"""
        You are an expert technical assistant. Answer the user's query based ONLY on the provided context.
        If the context does not contain the answer, say "I don't know based on the provided documents".
        Answer in the same language as the user's query.
        
        Context ({ev.source}):
        {ev.context}
        
        User Query: {ev.query}
        
        Answer:
        """
        
        # תוקן: שימוש ב-Chat API במקום ב-Generate API הישן
        messages = [ChatMessage(role="user", content=prompt)]
        response = await Settings.llm.achat(messages)
        
        # אנחנו מוסיפים תגית לתשובה כדי שנראה בממשק איזה נתיב נבחר!
        final_answer = f"{response.message.content}\n\n*(נשלף באמצעות: {ev.source})*"
        return StopEvent(result=final_answer)

# ---------------------------------------------------------
# 3. הפעלת המערכת והממשק
# ---------------------------------------------------------
def main():
    load_dotenv()
    unstrict_ssl()

    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

    Settings.embed_model = CohereEmbedding(
        api_key=COHERE_API_KEY,
     model_name="embed-english-v3.0",
    )
    Settings.llm = Cohere(
        api_key=COHERE_API_KEY, 
        model="command-r-08-2024"
    )

    print("מתחבר ל-Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    pinecone_index = pc.Index("rag-project")
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index, namespace="rag-project")
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # תוקן: קריאה נכונה ל-pinecone_index
    workflow = RoutingRAGWorkflow(pinecone_index=index, timeout=60.0)

    async def chat_interface(question):
        response = await workflow.run(query=question)
        return response

    demo = gr.Interface(
        fn=chat_interface,
        inputs=gr.Textbox(label="שאל שאלה על קבצי הפרויקט:", lines=2),
        outputs=gr.Textbox(label="תשובת המערכת:"),
        title="Agentic Coding RAG - Advanced Router 🔀",
        description="מערכת RAG חכמה עם נתב שמחליט האם לגשת לחיפוש וקטורי או לנתונים מובנים (JSON)."
    )
    draw_all_possible_flows(RoutingRAGWorkflow, filename="my_workflow.html")
    print("✅ תרשים הזרימה האוטומטי נשמר בקובץ my_workflow.html")
    print("מפעיל את ממשק הצ'אט...")
    demo.launch()

if __name__ == "__main__":
    main()