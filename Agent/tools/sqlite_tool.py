import sqlite3
import os
from typing import List, Tuple, Any

Database_path = r"C:\Users\HP\Desktop\Retail-Agent\AI-Assignment-Project\data\northwind.db"

def get_db_schema(tables: List[str] = None) -> str:
    """
    Retrieves the SQLite database schema for the given tables.
    If no tables are specified, it returns the schema for all important tables.
    """
    conn = None
    try:
        conn = sqlite3.connect(Database_path)
        cursor = conn.cursor()
        if tables is None:
            # if no tables list then read these automatically.
            tables = [
                "Orders", 
                "Order Details", 
                "Products", 
                "Customers", 
                "Categories",
                "Suppliers"
            ]
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = [row[0] for row in cursor.fetchall()]
        
        if 'orders' in views:
            tables.extend(['orders', 'order_items', 'products', 'customers'])


        schema = []
        for table_name in set(tables):
            try:
                
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns = [
                    f"{col[1]} {col[2]}" 
                    for col in cursor.fetchall()
                ]
                
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
                create_sql = cursor.fetchone()[0]
                
                schema.append(f"Table: {table_name}\nColumns: {', '.join(columns)}\nCREATE TABLE: {create_sql}\n")
            except Exception as e:
                print(f"We found error at : {e}")
        
        return "\n---\n".join(schema)

    except sqlite3.Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"File Error: Could not connect to database. Check path: {Database_path}. Error: {e}"
    finally:
        if conn:
            conn.close()

def execute_sql_query(query: str) -> Tuple[List[str], List[Any]]:
    """
    Executes a read-only SQL query and returns column names and results.
    Assumes only SELECT statements are passed.
    """
    conn = None
    try:
        conn = sqlite3.connect(Database_path)
        cursor = conn.cursor()
        query_upper = query.strip().upper()
        if not (query_upper.startswith("SELECT") or query_upper.startswith("PRAGMA") or query_upper.startswith("EXPLAIN")):
             raise ValueError("Only read-only SQL (SELECT) is allowed.")
        
        cursor.execute(query)
        
        columns = [description[0] for description in cursor.description]
        
        results = cursor.fetchall()
        
        return columns, results

    except sqlite3.Error as e:
        return ["Error"], [f"SQLITE_ERROR: {e}"]
    except Exception as e:
        return ["Error"], [f"PYTHON_ERROR: {e}"]
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Testing Schema Introspection")
    res = get_db_schema()


    print("Testing SQL Execution")
    test_query = "SELECT * FROM Customers WHERE CustomerID = 'BERGS';"
    cols, rows = execute_sql_query(test_query)
    print(f"Columns: {cols}")
    print(f"Results: {rows}")