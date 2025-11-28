from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

class RepairOutput(BaseModel):
    fixed_sql: Optional[str] = Field(
        default=None,
        description="Repaired SQL query if SQL was incorrect or failed."
    )
    reason: Optional[str] = Field(
        default=None,
        description="Short explanation of what was repaired."
    )
    retry_needed: bool = Field(
        default=False,
        description="True if another repair iteration should run."
    )


gemini = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=GROK_API_KEY,
    temperature=0
)

repair_model = gemini.with_structured_output(RepairOutput)

REPAIR_PROMPT = """
You are a repair engine for a Retail Analytics Agent.

Your task is to FIX SQL errors when SQL fails during execution.

RULES:
- Produce ONLY a corrected SQL query (SELECT-only, valid SQLite).
- Never generate DELETE, UPDATE, INSERT, DROP, ALTER, CREATE.
- Never output multiple statements.
- Use only the tables and schema provided.
- If planner info is missing, infer minimal fields from question.
- If SQL itself was empty, generate a brand new SQL safely.

INPUTS:
QUESTION:
{question}

PLANNER:
{planner}

FAILED_SQL:
{failed_sql}

SQL_ERROR:
{sql_error}

SCHEMA:
{schema}

OUTPUT REQUIREMENTS:
- fixed_sql: corrected SQL (empty if cannot fix)
- reason: why repair was needed
- retry_needed: true if another repair loop should run

Return JSON only.
"""

def run_repair(question: str, planner: Dict[str, Any], failed_sql: str, sql_error: str, schema: str) -> RepairOutput:
    prompt = REPAIR_PROMPT.format(
        question=question,
        planner=planner,
        failed_sql=failed_sql,
        sql_error=sql_error,
        schema=schema,
    )
    return repair_model.invoke(prompt)

def repair_loop(question: str, planner: Dict[str, Any], sql: str, sql_result: Dict[str, Any], schema: str):
    """
    Attempts repairing SQL up to 2 times.
    Returns final SQL (fixed or original) + a summary.
    """
    MAX_RETRIES = 2
    attempt = 0
    current_sql = sql
    final_reason = "No repair needed"

    while attempt < MAX_RETRIES:
        error = sql_result.get("error")
        if not error:
            break  # success, no need to repair

        print(f"Repair attempt {attempt + 1} for SQL error: {error}")
        
        output: RepairOutput = run_repair(
            question=question,
            planner=planner,
            failed_sql=current_sql,
            sql_error=error,
            schema=schema
        )

        if not output.fixed_sql:
            final_reason = "Repair model could not fix the SQL."
            break

        # Apply repaired SQL
        current_sql = output.fixed_sql
        final_reason = output.reason or "SQL repaired"

        # Test the repaired SQL
        from sqlite_tool import execute_sql_query
        try:
            columns, rows = execute_sql_query(current_sql)
            # If successful, update sql_result
            sql_result = {"columns": columns, "rows": rows, "error": None}
            break  # Success, exit loop
        except Exception as e:
            sql_result = {"error": str(e)}
            attempt += 1
            continue

    return {
        "sql": current_sql,
        "reason": final_reason,
        "attempts": attempt + 1,
        "success": not sql_result.get("error")
    }

if __name__ == "__main__":
    bad_sql = "SELECT * FRM Orders"  # purposely broken
    sql_result = {"error": "near 'FRM': syntax error"}

    planner_sample = {
        "kpi": "revenue",
        "category": "Beverages",
        "date_start": "1997-01-01",
        "date_end": "1997-02-01"
    }

    schema_text = "TABLE: Orders (...)"

    out = repair_loop(
        question="Revenue for Beverages?",
        planner=planner_sample,
        sql=bad_sql,
        sql_result=sql_result,
        schema=schema_text
    )

    print(out)