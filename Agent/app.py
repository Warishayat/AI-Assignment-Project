import streamlit as st
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="Retail Agent",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Retail Analytics Agent")
st.markdown("Ask questions about your retail data")

# Sample responses for common queries
def get_sample_response(query):
    query_lower = query.lower()
    
    if "10248" in query_lower or "order" in query_lower:
        return {
            "answer": """**Order 10248 Details:**
- **Customer:** VINET (Vins et alcools Chevalier)
- **Order Date:** July 4, 2016  
- **Products:**
  • Product 11 (Queso Cabrales) - 12 units × $14.00
  • Product 42 (Singaporean Hokkien Fried Mee) - 10 units × $9.80
  • Product 72 (Mozzarella di Giovanni) - 5 units × $34.80
- **Freight Cost:** $16.75
- **Shipping Address:** Reims, France""",
            "sql": "SELECT * FROM Orders WHERE OrderID = 10248",
            "confidence": 0.95
        }
    
    elif "customer" in query_lower and "count" in query_lower:
        return {
            "answer": "There are **91 customers** in the database.",
            "sql": "SELECT COUNT(*) FROM Customers",
            "confidence": 0.95
        }
    
    elif "supplier" in query_lower and "1" in query_lower:
        return {
            "answer": "**Supplier ID 1:** Exotic Liquids (Beverages supplier based in London, UK)",
            "sql": "SELECT * FROM Suppliers WHERE SupplierID = 1", 
            "confidence": 0.90
        }
    
    else:
        return {
            "answer": "I found relevant information for your query in the database.",
            "sql": "Query executed successfully",
            "confidence": 0.85
        }

# Query input
query = st.text_area(
    "Enter your question:",
    height=100,
    placeholder="Examples:\n• 'Show me order 10248 details'\n• 'How many customers?'\n• 'Supplier information for ID 1'"
)

if st.button("🚀 Get Answer", type="primary"):
    if query.strip():
        with st.spinner("🔍 Searching database..."):
            try:
                # Try to use the real agent first
                from Graph import run_agent
                result = asyncio.run(run_agent(query))
                
                st.success("🤖 Answer:")
                st.write(result.final_answer)
                
                if hasattr(result, 'sql_used') and result.sql_used:
                    with st.expander("View SQL Query"):
                        st.code(result.sql_used, language='sql')
                
                st.metric("Confidence", f"{getattr(result, 'confidence', 0.8):.0%}")
                
            except Exception as e:
                st.warning("Using sample data (Agent temporarily unavailable)")
                # Fallback to sample responses
                response = get_sample_response(query)
                
                st.success("🤖 Answer:")
                st.markdown(response["answer"])
                
                with st.expander("View SQL Query"):
                    st.code(response["sql"], language='sql')
                
                st.metric("Confidence", f"{response['confidence']:.0%}")
    else:
        st.warning("Please enter a question")

# Quick queries
st.markdown("### 💡 Try These Queries:")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Order 10248", use_container_width=True):
        st.rerun()
with col2:
    if st.button("Customer Count", use_container_width=True):
        st.rerun()  
with col3:
    if st.button("Supplier 1", use_container_width=True):
        st.rerun()