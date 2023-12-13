from langchain.chat_models import ChatOpenAI, ChatCohere
import os
from langchain.chat_models import ChatGooglePalm
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

os.environ["OPENAI_API_KEY"] = "YOUR OPENAI API KEY"
os.environ["COHERE_API_KEY"] = "YOUR COHERE API KEY"
os.environ["GOOGLE_API_KEY"] = "YOUR GOOGLE API KEY"

global models

def create_cot_chain(llm):
    thought_prompt = PromptTemplate.from_template(
        """ You are a synthetic biologist, follow the instructions and answer the questions
        {question}
        Let's think step by step """
    )

    answer_prompt = PromptTemplate.from_template(
        """
    {thought}
    Answer:"""
    )
    chain = (
        {"thought": thought_prompt | llm | StrOutputParser()}
        | answer_prompt
        | llm
        | StrOutputParser()
    )
    return chain

openai_35_llm = ChatOpenAI(temperature=0, model= "gpt-3.5-turbo-1106")
openai_4_llm = ChatOpenAI(temperature=0, model= "gpt-4")
cohere_llm = ChatCohere(temperature=0)
palm_llm = ChatGooglePalm(temperature=0, model = "chat-bison-001")
palm_chain = create_cot_chain(palm_llm)
openai_35_llm_chain = create_cot_chain(openai_35_llm)
openai_4_llm_chain = create_cot_chain(openai_4_llm)
cohere_llm_chain = create_cot_chain(cohere_llm)

models = {"openai-3.5-turbo": [openai_35_llm, openai_35_llm_chain], 
"openai-4": [openai_4_llm, openai_4_llm_chain], 
"cohere": [cohere_llm, cohere_llm_chain], 
"palm": [palm_llm, palm_chain]}