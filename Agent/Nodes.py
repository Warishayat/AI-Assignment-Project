from Classifier_route import classify_route
from planner import run_planner
from retrieval import init_retriever, retrieve
from sql_gen import generate_sql_async
from sqlite_tool import execute_sql_query, get_db_schema
from Synthesizer import run_synthesizer
from Repair_loop import repair_loop

# Initialize retriever once
docs, metadata, vectorizer, vectors = init_retriever()

async def router_node(state):
    """Classify the query route"""
    route = classify_route(state.question)
    state.route = route.upper()  # Convert to uppercase for consistency
    print(f"Router: classified as {state.route}")
    return state

async def retriever_node(state):
    """Retrieve relevant documents if needed"""
    if state.route == "SQL":
        state.rag_docs = []
        print("Retriever: SQL route, skipping document retrieval")
        return state

    print(f"Retriever: Retrieving documents for {state.route} route")
    results = retrieve(
        state.question,
        top_k=5,
        vectorizer=vectorizer,
        doc_vectors=vectors,
        docs=docs,
        metadata=metadata,
    )

    state.rag_docs = results
    print(f"Retriever: Retrieved {len(results)} documents")
    return state

async def planner_node(state):
    """Plan the execution based on question and documents"""
    rag_docs = state.rag_docs or []
    planner = run_planner(state.question, rag_docs)
    state.planner = planner
    print(f"Planner: need_sql={planner.need_sql}, need_rag={planner.need_rag}")
    return state

async def sql_gen_node(state):
    """Generate SQL if needed"""
    planner = state.planner

    if not planner or not planner.need_sql:
        state.sql = ""
        state.sql_explanation = "No SQL needed"
        print("SQL Gen: Skipping SQL generation")
        return state

    # Convert planner to dict for SQL generation
    planner_dict = {
        "kpi": planner.kpi,
        "category": planner.category,
        "event": planner.event,
        "date_start": planner.date_start,
        "date_end": planner.date_end,
        "need_sql": planner.need_sql,
        "need_rag": planner.need_rag
    }

    print("SQL Gen: Generating SQL...")
    sql_output = await generate_sql_async(state.question, planner_dict)
    
    state.sql = sql_output.sql
    state.sql_explanation = sql_output.plan_explanation
    print(f"SQL Gen: Generated SQL: {state.sql[:100]}..." if state.sql else "SQL Gen: No SQL generated")
    return state

async def sql_exec_node(state):
    """Execute the SQL query"""
    if not state.sql or not state.sql.strip():
        state.sql_result = {"rows": [], "columns": [], "error": None, "has_data": False}
        print("SQL Exec: No SQL to execute")
        return state

    print("SQL Exec: Executing SQL...")
    try:
        columns, rows = execute_sql_query(state.sql)
        state.sql_result = {
            "columns": columns, 
            "rows": rows, 
            "error": None,
            "has_data": len(rows) > 0
        }
        print(f"SQL Exec: Success - {len(rows)} rows returned")
    except Exception as e:
        state.sql_result = {"error": str(e), "has_data": False}
        print(f"SQL Exec: Error - {str(e)}")

    return state

async def synth_node(state):
    """Synthesize the final answer"""
    print("Synthesizer: Creating final answer...")
    
    # Convert planner to dict for synthesizer
    planner_dict = {}
    if state.planner:
        planner_dict = {
            "kpi": state.planner.kpi,
            "category": state.planner.category,
            "event": state.planner.event,
            "date_start": state.planner.date_start,
            "date_end": state.planner.date_end,
            "need_sql": state.planner.need_sql,
            "need_rag": state.planner.need_rag
        }

    answer = run_synthesizer(
        question=state.question,
        planner=planner_dict,
        sql=state.sql,
        sql_result=state.sql_result or {},
        docs=state.rag_docs or []
    )

    state.final_answer = answer
    print("Synthesizer: Final answer created")
    return state

async def repair_node(state):
    """Repair SQL if execution failed"""
    if not state.sql_result or not state.sql_result.get("error"):
        print("Repair: No error to repair")
        return state

    print("Repair: Attempting to repair SQL...")
    schema = get_db_schema()
    
    # Convert planner to dict
    planner_dict = {}
    if state.planner:
        planner_dict = {
            "kpi": state.planner.kpi,
            "category": state.planner.category,
            "event": state.planner.event,
            "date_start": state.planner.date_start,
            "date_end": state.planner.date_end,
            "need_sql": state.planner.need_sql,
            "need_rag": state.planner.need_rag
        }

    repaired = repair_loop(
        question=state.question,
        planner=planner_dict,
        sql=state.sql,
        sql_result=state.sql_result,
        schema=schema,
    )

    state.sql = repaired["sql"]
    state.repair_info = repaired
    state.retries += 1
    print(f"Repair: Repair completed - {repaired['reason']}")
    return state