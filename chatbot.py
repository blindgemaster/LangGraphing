from typing import Dict, TypedDict, List, Union
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


class AgentState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]
    



llm = ChatOpenAI(model="gpt-5.4-nano")


def message_platform(state: AgentState) -> AgentState:
    response = llm.invoke(state['messages'])
    state['messages'].append(AIMessage(content=response.content))
    print(f"AI Message: {response.content}")
    return state



graph = StateGraph(AgentState)

graph.add_node("Platform", message_platform)
graph.set_entry_point("Platform")
graph.set_finish_point("Platform")



agent =  graph.compile()
history = open("logging.txt", "r", encoding="utf-8")


conversation_history = [history for history in history.read().splitlines() if history.strip()]
print("conversation_history: ", conversation_history)
user_input = input("You: ")

while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))

    result = agent.invoke({"messages": conversation_history})

    print(result["messages"])
    conversation_history = result["messages"]
    
    
    user_input= input("You: ")


with open("logging.txt", "w", encoding="utf-8") as file:
    file.write("Your Conversation History:\n")

    for message in conversation_history:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n\n")
    file.write("End of Conversation\n")

print("Conversation history has been saved to logging.txt")
        

