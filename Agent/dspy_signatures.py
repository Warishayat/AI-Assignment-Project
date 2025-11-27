from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import Literal

class RouterOutput(BaseModel):
    route: Literal["sql", "rag", "hybrid"] 


model = ChatOllama(
    model="phi3.5:3.8b-mini-instruct-q4_K_M",
    temperature=0,
)

parser = PydanticOutputParser(pydantic_object=RouterOutput)

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a routing engine. Determine the correct route based on the question.\n"
     "Routes:\n"
     "- sql → database, tables, KPIs, metrics, dates, sales, products\n"
     "- rag → policies, definitions, documentation, catalog\n"
     "- hybrid → both SQL and policy needed\n\n"
     "Return JSON that matches the required format."
    ),
    ("human", "{question}\nFormat Instructions:\n{format_instructions}")
])

# Combine everything
router_chain = prompt | model | parser


def router_predict(question: str) -> RouterOutput:
    return router_chain.invoke({
        "question": question,
        "format_instructions": parser.get_format_instructions()
    })


# Terminal Loop
if __name__ == "__main__":
    print("\nRouter test...\n")
    while True:
        q = input("Ask: ")
        if q in ["exit", "quit"]:
            break
        print("ROUTE:", router_predict(q).route)
        print("-" * 40)
