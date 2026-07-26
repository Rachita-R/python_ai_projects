from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_groq import ChatGroq
import os
load_dotenv()


@tool
def calculator(a:float, b:float) -> str:
    """Calculate the sum of two numbers."""
    return f"The sum of {a} and {b} is {a + b}."


@tool
def say_hello(name:str) -> str:
    """Say hello to the user."""
    return f"Hello {name}, I hope you are well today!"


def main():
    model = ChatGroq(
        model="openai/gpt-oss-120b", 
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )
    tools = [calculator, say_hello]
    agent_executor = create_react_agent(model, tools)
    print("Welcome to the React Agent! Type 'exit' to quit.")
    print("You can ask questions or give commands to the agent.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "quit":
            break

        print("\nAssistant: ", end="")
        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=user_input)]}
        ):
            if "agent" in chunk and "messages" in chunk["agent"]:
                for message in chunk["agent"]["messages"]:
                    print(message.content, end="")
        print()


if __name__ == "__main__":
    main()