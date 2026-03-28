from typing import Annotated, Sequence
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import TypedDict

load_dotenv()
print("[INIT] Environment loaded.")

llm = ChatOpenAI(model="gpt-5.4-nano")
print("[INIT] LLM ready.")


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def fix_txt_file(human_message: str, text_file: str) -> str:
    """Fix the text file according to the Human message and return the fixed text file."""
    print(f"[TOOL] fix_txt_file called on '{text_file}'")
    with open(text_file, "r") as f:
        content = f.read()
    print(f"[TOOL] File read ({len(content)} chars). Sending to LLM...")
    result = llm.invoke([
        SystemMessage(content="You are a file editor. Return ONLY the updated file content with no explanations, no markdown, no backticks, no extra text. Just the raw file content."),
        HumanMessage(content=f"{human_message}\n\nFile content:\n{content}")
    ])
    with open(text_file, "w") as f:
        f.write(result.content)
    print(f"[TOOL] File updated and saved: '{text_file}'")
    return text_file


tools = [fix_txt_file]
llm_with_tools = ChatOpenAI(model="gpt-5.4-nano").bind_tools(tools)
print("[INIT] Tools bound to LLM.")


def agent_node(state: AgentState) -> AgentState:
    print("[AGENT] Thinking...")
    system_prompt = SystemMessage(content="You are a helpful assistant that drafts a document until the human is happy with the document")
    response = llm_with_tools.invoke([system_prompt] + list(state["messages"]))
    if response.tool_calls:
        print(f"[AGENT] Decided to use tool: {response.tool_calls[0]['name']}")
    else:
        print(f"[AGENT] Response: {response.content}")
    return {"messages": [response]}


def human_node(state: AgentState) -> AgentState:
    print("\n[HUMAN] Your turn. (type 'exit' to quit)")
    user_input = input("You: ").strip()
    if user_input.lower() in ("exit", "quit", "q"):
        print("[DONE] Exiting. Goodbye!")
        raise SystemExit(0)
    return {"messages": [HumanMessage(content=user_input)]}


def decider(state: AgentState):
    last = state["messages"][-1]
    if isinstance(last, HumanMessage):
        print("[DECIDER] Human message → routing to Agent")
        return "agent"
    elif isinstance(last, AIMessage) and last.tool_calls:
        print("[DECIDER] Tool call detected → routing to Tool")
        return "tool"
    else:
        print("[DECIDER] Agent done → routing back to Human")
        return "human"


main_graph = StateGraph(AgentState)
main_graph.add_node("Agent", agent_node)
main_graph.add_node("Human", human_node)
main_graph.add_node("Tool", ToolNode(tools))

main_graph.set_entry_point("Human")
main_graph.add_conditional_edges("Human", decider, {"agent": "Agent"})
main_graph.add_conditional_edges("Agent", decider, {"tool": "Tool", "human": "Human"})
main_graph.add_edge("Tool", "Agent")

graph = main_graph.compile()
print("[INIT] Graph compiled and ready.\n")

if __name__ == "__main__":
    print("=" * 40)
    print("  Drafting Agent with Human Input")
    print("=" * 40)
    print("Type your drafting request to begin.\n")
    graph.invoke({"messages": []})
