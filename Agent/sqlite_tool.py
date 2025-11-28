import sqlite3
import os
from typing import List, Tuple, Any

Database_path = r"C:\Users\HP\Desktop\Retail-Agent\AI-Assignment-Project\data\northwind.db"

def get_db_schema(tables: List[str] = None) -> str:
    """
    Retrieves the SQLite database schema for the given tables.
    """
    conn = None
    try:
        conn = sqlite3.connect(Database_path)
        cursor = conn.cursor()
        
        if tables is None:
            tables = [
                "Orders", 
                "Order Details", 
                "Products", 
                "Customers", 
                "Categories",
                "Suppliers"
            ]

        schema_parts = []
        
        for table_name in set(tables):
            try:
                # Get column info
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns_info = cursor.fetchall()
                
                if not columns_info:
                    continue
                    
                columns = [f"{col[1]} ({col[2]})" for col in columns_info]
                
                # Get sample data count
                cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
                count = cursor.fetchone()[0]
                
                schema_parts.append(f"Table: {table_name}")
                schema_parts.append(f"Row count: {count}")
                schema_parts.append(f"Columns: {', '.join(columns)}")
                schema_parts.append("")  # empty line
                
            except Exception as e:
                schema_parts.append(f"Table: {table_name} - Error: {str(e)}")
                continue

        return "\n".join(schema_parts) if schema_parts else "No schema information available"

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
    """
    conn = None
    try:
        conn = sqlite3.connect(Database_path)
        cursor = conn.cursor()
        
        query_upper = query.strip().upper()
        if not (query_upper.startswith("SELECT") or query_upper.startswith("PRAGMA") or query_upper.startswith("EXPLAIN")):
            raise ValueError("Only read-only SQL (SELECT/PRAGMA/EXPLAIN) is allowed.")
        
        cursor.execute(query)
        
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        
        return columns, results

    except sqlite3.Error as e:
        raise Exception(f"SQLITE_ERROR: {e}")
    except Exception as e:
        raise Exception(f"PYTHON_ERROR: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Testing Schema Introspection")
    schema = get_db_schema()
    print("Schema:", schema[:500] + "..." if len(schema) > 500 else schema)

    print("\nTesting SQL Execution")
    test_query = "SELECT CustomerID, CompanyName FROM Customers LIMIT 3;"
    try:
        cols, rows = execute_sql_query(test_query)
        print(f"Columns: {cols}")
        print(f"Results: {rows}")
    except Exception as e:
        print(f"Error: {e}")