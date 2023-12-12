from typing import Optional, Callable, Dict, Iterable
import ast
import contextlib
import faulthandler
import io
import os
import multiprocessing
import platform
import signal
import tempfile
import gzip
import json
import os
from langchain.agents import AgentType, Tool, initialize_agent, load_tools
from langchain.chat_models import ChatOpenAI, ChatCohere
from getpass import getpass
from langchain.chat_models import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
import google.generativeai as palm
from langchain.chat_models import ChatGooglePalm
import pandas as pd


def stream_jsonl(filename: str) -> Iterable[Dict]:
    """
    Parses each jsonl line and yields it as a dictionary
    """
    if filename.endswith(".gz"):
        with open(filename, "rb") as gzfp:
            for line in fp:
                if any(not x.isspace() for x in line):
                    yield json.loads(line)
    else:
        with open(filename, "r") as fp:
            for line in fp:
                if any(not x.isspace() for x in line):
                    yield json.loads(line)


def check_correctness_llm(llm, problem: Dict, trial: int, timeout: float,
                      completion_id: Optional[int] = None) -> Dict:
    """
    Evaluates the functional correctness of a completion by running the test
    suite provided in the problem. 

    :param completion_id: an optional completion ID so we can match
        the results later even if execution finishes asynchronously.
    """
    print(problem["task_id"])
    try: 
        result = llm.invoke(str(problem['prompt']))
    except Exception as e:
        print(e)
        return dict(
        task_id= problem["task_id"],
        test_type = "regular",
        passed= "DID NOT COMPLETE",
        result= "",
        solution = problem["solution"],
        completion_id=trial,
    )
    parser = StrOutputParser()
    answer = parser.invoke(result)
    return dict(
        task_id= problem["task_id"],
        test_type = "regular",
        passed= answer == problem['solution'],
        result= answer,
        solution = problem["solution"],
        completion_id=trial,
    )

def check_correctness_llm_chain (chain, problem: Dict, trial: int, timeout: float,
                      completion_id: Optional[int] = None) -> Dict:
    
    print(problem["task_id"])
    try:
        result = chain.invoke({'question': str(problem['prompt'])})
    except Exception as e:
        print(e)
        return dict(
        task_id= problem["task_id"],
        test_type = "regular",
        passed= "DID NOT COMPLETE",
        result= "",
        solution = problem["solution"],
        completion_id=trial,
        )
    return dict(
        task_id=problem["task_id"],
        test_type = "cot",
        passed= result == problem["solution"],
        result= result,
        solution = problem["solution"],
        completion_id= trial,
    )

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
    

if __name__ == "__main__":
    
    palm_chain = create_cot_chain(palm_llm)
    openai_35_llm_chain = create_cot_chain(openai_35_llm)
    openai_4_llm_chain = create_cot_chain(openai_4_llm)
    cohere_llm_chain = create_cot_chain(cohere_llm)
    
    models = {"cohere": [cohere_llm, cohere_llm_chain]}

    #models = {"openai-3.5-turbo": [openai_35_llm, openai_35_llm_chain], "openai-4": [openai_4_llm, openai_4_llm_chain], "cohere": [cohere_llm, cohere_llm_chain], "palm": [palm_llm, palm_chain]}
    results = {}
        
    for model in models:
        result = []
        if model not in results:
            results[model] = pd.DataFrame(columns = ["task_id", "test_type", "passed", "result", "solution", "completion_id"])
        for i in [0, 1, 2]:
            suite = stream_jsonl('synbioEval.jsonl')
            for item in suite:
                result.append(check_correctness_llm(models[model][0], problem=item, trial= i+1, timeout=10))
                result.append(check_correctness_llm_chain(models[model][1], problem=item, trial = i+1, timeout=10))
        for data_dict in result:
            df_temp = pd.DataFrame([data_dict])
            results[model] = pd.concat([results[model], df_temp], ignore_index=True)
        results[model].to_csv(f"results/{model}.csv")
