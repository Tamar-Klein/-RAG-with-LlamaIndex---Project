"""
=============================================================================
הערה חשובה: 
קובץ זה (app.py) מהווה את שלב א' (MVP) של הפרויקט ומשמש כבסיס בלבד.
הוא מדגים הקמת מערכת RAG בסיסית בגישת "קופסה שחורה" (Query Engine רגיל).
הקובץ נשמר בפרויקט לצורך תיעוד התהליך הלימודי והשוואה לארכיטקטורה המתקדמת.

👉 להרצת הפרויקט המלא והעדכני, הכולל ארכיטקטורת Event-Driven, 
    חילוץ נתונים מובנים (JSON) ונתב (Router) חכם — אנא השתמשו בקובץ `agent.py`.
=============================================================================
"""

import os
from dotenv import load_dotenv
from netfree_unstrict_ssl import unstrict_ssl
import gradio as gr

from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere

# 1. טעינת משתני סביבה
load_dotenv()
unstrict_ssl()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# 2. הגדרת המודלים
# מודל ה-Embedding מתרגם את השאלה שלך לוקטור כדי שיוכל לחפש ב-Pinecone
Settings.embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",
)

# מודל ה-LLM קורא את התוצאות מהחיפוש ומנסח לך תשובה בעברית/אנגלית
Settings.llm = Cohere(
    api_key=COHERE_API_KEY, 
    model="command-r-08-2024"
)

# 3. התחברות ל-Pinecone
print("מתחבר למסד הנתונים ב-Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("rag-project")

# חשוב: אנחנו מציינים את ה-Namespace שבו נמצאים הנתונים שלנו
vector_store = PineconeVectorStore(pinecone_index=pinecone_index, namespace="rag-project")

# הפעם רק קוראים את האינדקס הקיים, לא יוצרים מחדש
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

# הגדרת מנוע החיפוש - מבקשים שיביא את 3 המקטעים הכי רלוונטיים לשאלה
query_engine = index.as_query_engine(similarity_top_k=5)

# 4. הפונקציה שתופעל כשתשאלי שאלה בממשק
def ask_rag(question):
    if not question.strip():
        return "אנא הקלד שאלה."
    
    print(f"מחפש תשובה לשאלה: {question}")
    response = query_engine.query(question)
    return str(response)

# 5. יצירת הממשק הגרפי
demo = gr.Interface(
    fn=ask_rag,
    inputs=gr.Textbox(label="שאל שאלה על קבצי הפרויקט:", lines=2),
    outputs=gr.Textbox(label="תשובת המערכת:"),
    title="Agentic Coding RAG",
    description="מערכת RAG לתשאול מסמכי תיעוד וארכיטקטורה. נסה לשאול על המערכת!"
)

if __name__ == "__main__":
    print("מפעיל את ממשק הצ'אט...")
    demo.launch()