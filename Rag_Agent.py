from typing import Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import TypedDict
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import os

load_dotenv()

llm = ChatOpenAI(model="gpt-5.4-nano", temperature=0)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small",)

pdf_path = "example.pdf"


if not os.path.exists(pdf_path):
    print(f"[ERROR] PDF file '{pdf_path}' not found. Please make sure it exists in the current directory.")
    raise FileNotFoundError(f"PDF file '{pdf_path}' not found.")


persist_directory = r"C:\Users\ka448\GoogleSDK\chroma_db"
collection_name = "pdf_docs"

chroma_exists = os.path.exists(persist_directory) and os.path.isdir(persist_directory) and len(os.listdir(persist_directory)) > 0

if chroma_exists:
    print(f"[INIT] Vector store already exists. Skipping embedding.")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=collection_name
    )
else:
    pdf_loader = PyPDFLoader(pdf_path)
    try:
        documents = pdf_loader.load()
        print(f"[INIT] PDF loaded successfully. {len(documents)} pages found.")
    except Exception as e:
        print(f"[ERROR] Failed to load PDF: {e}")
        raise

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    document_split = text_splitter.split_documents(documents)

    os.makedirs(persist_directory, exist_ok=True)
    try:
        vectorstore = Chroma.from_documents(
            documents=document_split,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name
        )
        print(f"[INIT] Vector store created and documents embedded successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to create vector store: {e}")
        raise

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})



@tool
def retrieve_pdf_info(query: str) -> str:
    """Retrieve relevant information from the PDF based on the query."""
    print(f"[TOOL] retrieve_pdf_info called with query: '{query}'")
    results = retriever.invoke(query)
    if not results:
        print("[TOOL] No relevant documents found.")
        return "No relevant information found in the PDF."
    combined_content = "\n\n".join([doc.page_content for doc in results])
    print(f"[TOOL] Retrieved {len(results)} relevant documents. Combined content length: {len(combined_content)} chars.")
    return combined_content


tools = [retrieve_pdf_info]
llm_with_tools = ChatOpenAI(model="gpt-5.4-nano", temperature=0).bind_tools(tools)
print("[INIT] Tools bound to LLM.")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


tools_dict = {our_tool.name: our_tool for our_tool in tools}

def should_continue(state: AgentState):
    """Check if the last message contains tool calls"""
    result = state["messages"][-1]
    return hasattr(result, "tool_calls") and len(result.tool_calls) > 0

system_prompt = SystemMessage(content="You are a helpful assistant that answers questions based on the provided PDF information. Use the 'retrieve_pdf_info' tool to get relevant information from the PDF when needed.")
def call_llm(state: AgentState) -> AgentState:
    """Function to call the LLM with the current state"""
    
    messages = list(state["messages"])
    messages = [SystemMessage(content=system_prompt.content)] + messages   
    message = llm_with_tools.invoke(messages)
    return {"messages": [message]}

def take_action(state: AgentState) -> AgentState:
    """Function to take action based on the tool calls in the last message"""
    tool_calls = state["messages"][-1].tool_calls
    results = []
    for t in tool_calls:
        print(f"[AGENT] Executing tool: {t['name']} with input: {t['args'].get('query', 'No query provided')}")
        if not t['name'] in tools_dict:
            print(f"[ERROR] Tool '{t['name']}' not found in tools_dict.")
            result = "Error: Tool not found."
        else:
            result = tools_dict[t['name']].invoke(t["args"].get("query", ""))
            print (f"Result length: {len(str(result))}")

        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    print("Tools executed. Returning results to LLM.")
    return {"messages": results}





graph = StateGraph(AgentState)

graph.add_node("agent", call_llm)
graph.add_node("retriever_agent", take_action)
graph.add_conditional_edges(
    "agent",
    should_continue,
    {True: "retriever_agent", False: END}
)

graph.add_edge("retriever_agent", "agent")
graph.set_entry_point("agent")

rag_agent = graph.compile()



def running_agent():
    print("=============RAG Agent Started=============")
    while True:
        user_input = input("Ask a question about the PDF (or type 'exit' to quit): ")
        if user_input.lower() in ("exit", "quit", "q"):
            print("[DONE] Exiting. Goodbye!")
            return 
        messages = [HumanMessage(content=user_input)]
        result = rag_agent.invoke({"messages": messages})

        print("\n[AGENT RESPONSE]")
        print(result["messages"][-1].content)


running_agent()


