from typing import Optional, Callable, Dict, Iterable
from pathlib import Path
import sys
import json
import os
from langchain.chat_models import ChatOpenAI, ChatCohere
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.chat_models import ChatGooglePalm
import pandas as pd
from models_setup import models

results = {}

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
                      model_name) -> Dict:
    """
    Evaluates the functional correctness of a completion by running the test
    suite provided in the problem. 
    """
    print(f"{problem["task_id"]} with {model_name} regular")
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
                      model_name) -> Dict:
    
    print(f"{problem["task_id"]} with {model_name} CoT")
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

def process_model(model, test_name):
    result = []
    if model not in results:
        results[model] = pd.DataFrame(columns = ["task_id", "test_type", "passed", "result", "solution", "completion_id"])
    
    log_filename = f"log/log_{model}_{test_name}.txt"
    with open(log_filename, 'w') as log_file:
        sys.stdout = log_file   
        for i in [0, 1, 2]:
            suite = stream_jsonl(sys.argv[1])
            for item in suite:
                result.append(check_correctness_llm(models[model][0], problem=item, trial= i+1, timeout=5000, model_name=model))
                result.append(check_correctness_llm_chain(models[model][1], problem=item, trial = i+1, timeout=5000, model_name = model))
        for data_dict in result:
            df_temp = pd.DataFrame([data_dict])
            results[model] = pd.concat([results[model], df_temp], ignore_index=True)
        results[model].to_csv(f"results/{test_name}_{model}.csv")
        print(f"Process for model {model} completed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Please input a jsonl file with benchmarking tests.")
    
    test_path = Path(sys.argv[1])
    test_name = test_path.stem
    with open(test_path, 'r') as file:
        line_count = sum(1 for line in file)
    processes = []
    for model in models:
        process = multiprocessing.Process(target=process_model, args=(model, test_name))
        processes.append(process)
        process.start()
    for process in processes:
        process.join(line_count * 300)
    print("benchmarking tests completed!")