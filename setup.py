from langchain.agents import AgentType, Tool, initialize_agent, load_tools
from langchain.chat_models import ChatOpenAI
import os
# os.environ['OPENAI_API_KEY'] = "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"




if __name__ == "__main__":
    openai_35_llm = ChatOpenAI(temperature=0, model= "gpt-3.5-turbo-1106")