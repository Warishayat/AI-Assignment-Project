from pydantic import BaseModel, Field
from typing import Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

class QueryClassify(BaseModel):
    route: Literal["rag", "sql", "hybrid"] = Field(
        description="Classify the user query: rag, sql, or hybrid"
    )

ROUTER_PROMPT = """
You are an expert router for a Retail Analytics Agent.

Classify the user's question into EXACTLY ONE of these routes:
1. rag     → use ONLY documents (policies, events, catalog, KPI definitions)  
2. sql     → use ONLY database SQL (numeric facts, orders, sales, quantities)  
3. hybrid  → needs BOTH documents (for definitions/dates/categories) AND SQL for numbers.

Rules:
- If question asks about definitions, events, policy → rag  
- If question is purely numeric ("revenue", "top sellers", "quantity") → sql  
- If the question mixes doc info + SQL info → hybrid  
- If question mentions both "tables" and "events/dates/policies" → hybrid  

Return ONLY: rag, sql, or hybrid.
User Question:
{query}
"""

GROK_API_KEY = os.getenv("GROK_API_KEY")

gemini = ChatGroq(
    model="gemini-2.5-flash",
    api_key=GROK_API_KEY,
    temperature=0
)

router_model = gemini.with_structured_output(QueryClassify)

def classify_route(query: str) -> str:
    prompt = ROUTER_PROMPT.format(query=query)
    result = router_model.invoke(prompt)
    return result.route  

if __name__ == "__main__":
    query = "Bring the Document from the customer table and check what is the start date in the document of event"
    res = classify_route(query)
    print("ROUTE:", res)