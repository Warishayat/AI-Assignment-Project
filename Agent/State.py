from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AgentState(BaseModel):
    # Input
    question: str = Field(default="", description="User's natural language question")
    
    # Router
    route: Optional[str] = Field(
        default=None,
        description="Route chosen by classifier: RAG, SQL, or HYBRID"
    )
    
    # Retrieval
    rag_docs: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Retrieved document chunks from RAG retriever"
    )
    
    # Planner
    planner: Optional[Any] = Field(
        default=None,
        description="Planner output object (KPI, dates, category, etc.)"
    )
    
    # SQL
    sql: Optional[str] = Field(
        default=None,
        description="Generated SQL query"
    )
    
    sql_explanation: Optional[str] = Field(
        default=None,
        description="Explanation of SQL based on planner fields"
    )
    
    # SQL execution
    sql_result: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Results of SQL execution: rows, columns, error"
    )
    
    # Synthesize output
    final_answer: Optional[Any] = Field(
        default=None,
        description="Final synthesized answer returned to user"
    )
    
    # Repair
    repair_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Details about any SQL repair attempts"
    )
    
    # Flow control
    retries: int = Field(
        default=0,
        description="How many times repair loop has been attempted"
    )