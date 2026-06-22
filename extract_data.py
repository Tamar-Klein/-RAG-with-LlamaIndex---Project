import os
import json
from dotenv import load_dotenv
from netfree_unstrict_ssl import unstrict_ssl
from pydantic import BaseModel, Field
from typing import List

from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.llms.cohere import Cohere
from llama_index.core.program import LLMTextCompletionProgram

# 1. טעינת סביבה
load_dotenv()
unstrict_ssl()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

Settings.llm = Cohere(
    api_key=COHERE_API_KEY, 
    model="command-r-08-2024"
)

# 2. הגדרת הסכמות (Schemas) - אומרים ל-LLM בדיוק מה לחפש
class Rule(BaseModel):
    id: str = Field(..., description="Unique identifier for the rule (e.g., rule-001)")
    description: str = Field(..., description="The actual rule or guideline")
    area: str = Field(..., description="Area of the system (e.g., UI, Backend, DB)")

class Decision(BaseModel):
    id: str = Field(..., description="Unique identifier for the decision (e.g., dec-001)")
    description: str = Field(..., description="The architecture or technical decision made")
    reasoning: str = Field(..., description="Why this decision was made")

class OpenBug(BaseModel):
    id: str = Field(..., description="Unique identifier for the bug (e.g., bug-001)")
    description: str = Field(..., description="Description of the known issue or bug")
    status: str = Field(..., description="Current status of the bug")

class ExtractedData(BaseModel):
    rules: List[Rule] = Field(default_factory=list, description="List of all UI, technical or system rules")
    decisions: List[Decision] = Field(default_factory=list, description="List of architecture and technical decisions")
    open_bugs: List[OpenBug] = Field(default_factory=list, description="List of open bugs and known issues")

# 3. הגדרת התוכנית לחילוץ נתונים
prompt_template_str = """
Please extract structured data from the following text based on the requested schema.
If a certain type of information (rules, decisions, bugs) is not present, leave its list empty.
Return ONLY valid JSON matching the schema.

Text:
{text}
"""

# אנחנו משתמשים בתוכנית שמנחה את ה-LLM לחלץ את הנתונים לפי הסכמה שהגדרנו
program = LLMTextCompletionProgram.from_defaults(
    output_cls=ExtractedData,
    prompt_template_str=prompt_template_str,
    verbose=True,
)

# 4. ביצוע החילוץ
def run_extraction():
    print("קורא מסמכים לטובת חילוץ נתונים מובנים...")
    reader = SimpleDirectoryReader(
        input_dir="bakery-rag",
        recursive=True,         
        exclude_hidden=False   
    )
    documents = reader.load_data()
    
    # מאחדים את כל הטקסט כדי שה-LLM יוכל לעבור על כולו ולחלץ
    full_text = "\n".join([doc.text for doc in documents])
    
    print("שולח בקשה לחילוץ נתונים מובנים (זה עשוי לקחת חצי דקה)...")
    try:
        # הפעלת תוכנית החילוץ
        result = program(text=full_text)
        
        # המרת התוצאה (Pydantic object) למילון (Dictionary)
        result_dict = result.dict()
        
        # שמירת המילון לקובץ JSON
        output_file = "extracted_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=4, ensure_ascii=False)
            
        print(f"✅ חילוץ הנתונים עבר בהצלחה! הנתונים נשמרו בקובץ: {output_file}")
    except Exception as e:
         print(f"❌ שגיאה בחילוץ: {e}")

if __name__ == "__main__":
    run_extraction()
    