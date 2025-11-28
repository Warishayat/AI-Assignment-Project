import streamlit as st
import asyncio
import traceback
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Graph import run_agent

st.set_page_config(page_title="Debug Agent", layout="wide")

def debug_agent(query):
    """Debug version to catch exact errors"""
    try:
        st.write("🔍 **Debug Info:**")
        st.write(f"Query: `{query}`")
        
        # Test basic imports
        st.write("✅ Basic imports working")
        
        # Test agent execution
        st.write("🚀 Attempting to run agent...")
        result = asyncio.run(run_agent(query))
        
        st.write("✅ Agent executed successfully!")
        return result
        
    except ImportError as e:
        st.error(f"❌ Import Error: {e}")
        st.code(traceback.format_exc())
    except Exception as e:
        st.error(f"❌ Execution Error: {e}")
        st.code(traceback.format_exc())
    
    return None

# Streamlit app
st.title("🐛 Agent Debugger")

query = st.text_input("Enter query:", "find me record of id 10248 from the database?")

if st.button("Debug Query"):
    result = debug_agent(query)
    if result:
        st.success("✅ Query successful!")
        st.json(result.dict() if hasattr(result, 'dict') else str(result))