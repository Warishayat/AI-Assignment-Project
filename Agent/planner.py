from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from typing import Optional

load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

class PlannerOutput(BaseModel):
    kpi: Optional[str] = Field(
        default=None,
        description="The KPI requested (e.g., revenue, quantity, orders, top_products)."
    )
    category: Optional[str] = Field(
        default=None,
        description="Product category requested, if any (e.g., Beverages)."
    )
    event: Optional[str] = Field(
        default=None,
        description="Marketing event or campaign mentioned in the question, if any."
    )
    date_start: Optional[str] = Field(
        default=None,
        description="Start date (YYYY-MM-DD)."
    )
    date_end: Optional[str] = Field(
        default=None,
        description="End date (YYYY-MM-DD)."
    )
    need_sql: bool = Field(
        default=False,
        description="True if SQL is required for this query."
    )
    need_rag: bool = Field(
        default=False,
        description="True if RAG documents are required for this query."
    )

PLANNER_PROMPT = """
You are the planner for a Retail Analytics Agent.

Your job is to analyze the user QUESTION + the RAG DOCUMENT CHUNKS
and determine exactly what information is needed.

---------------------------------------
DETECT KPI (EXTREMELY IMPORTANT):
Mark need_sql = true whenever the user asks for anything numeric:
- revenue
- sales
- total sales
- quantity
- units sold
- count
- order count
- top products
- top selling
- performance
- profit
These KPIs ALWAYS require SQL.

DETECT RAG NEED:
Mark need_rag = true whenever:
- A campaign/event is mentioned
- Category description is required
- Promotion details are needed
- Dates must come from documents
- Any information appears only in RAG chunks

HYBRID rules:
If both numerical KPI + event/category/document data required → need_sql = true AND need_rag = true.

---------------------------------------

Extract the following fields:

- kpi → revenue, quantity, orders, top_products, etc.
- category → product category referenced by user.
- event → campaign or promotion name.
- date_start/date_end → MUST come from the RAG docs if an event is mentioned.

---------------------------------------

Return JSON only.
QUESTION:
{question}

DOCUMENT CHUNKS:
{docs}
"""

gemini = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=GROK_API_KEY,
    temperature=0
)


planner_model = gemini.with_structured_output(PlannerOutput)

def run_planner(question: str, rag_docs: list):
    doc_text = "\n\n".join([d["text"] for d in rag_docs]) if rag_docs else "No documents retrieved"
    prompt = PLANNER_PROMPT.format(
        question=question,
        docs=doc_text
    )
    result: PlannerOutput = planner_model.invoke(prompt)
    return result

if __name__ == "__main__":
    example_docs = [
        {"text": "Summer Spice Campaign runs from 1997-06-01 to 1997-06-30.", "source": "marketing_calendar.md"}
    ]
    res = run_planner("Revenue for Beverages during Summer Spice Campaign", example_docs)
    print(res)