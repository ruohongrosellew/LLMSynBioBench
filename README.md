# SynBioBench
Final Project for BioE 134: Synthetic Biology Benchmarking for Large Language Models
## Table of Contents
- [SynBioBench](#synbiobench)
  - [Table of Contents](#table-of-contents)
  - [How to run](#how-to-run)
    - [Setting Up Environment](#setting-up-environment)
    - [Set up your API keys](#set-up-your-api-keys)
    - [Running the Benchmarking Tests](#running-the-benchmarking-tests)
    - [Adding Models](#adding-models)
    - [Adding Tests](#adding-tests)
  - [Benchmarking Design](#benchmarking-design)
  - [Results](#results)
  - [Limitations](#limitations)
  - [Things to improve](#things-to-improve)
  - [Author](#author)
  - [Acknowledgements and Cited Work](#acknowledgements-and-cited-work)

## How to run
### Setting Up Environment
1. Clone this repository
2. Create a virtual environment and activate it
```
python -m venv /path/to/new/venv
source /path/to/new/venv/bin/activate
```
3. Install the packages listed in **requirements.txt**
```
pip install -r requirements.txt
```
**OR**
1. Make sure you have installed miniconda in your local environment
2. Create a new conda environment and activate it
```
conda env create -f environment.yml
conda activate synbiobench
```

### Set up your API keys


### Running the Benchmarking Tests
In the virtual python environment/conda environment, run the following command:
`python execution.py`
This automatically runs the benchmarking tests and saves the results by model in csv format under results directory.


### Adding Models
This benchmarking test suite use the langchain chat models interface to call chat models and create sequential chains using the LLMs. First, check if the model is supported by Langchain, follow the instructions and pattermatch the first severals lines in Main in **execution.py**. 


### Adding Tests
If you want to add any new tests, you can add them in the **synbioEval.jsonl** file. Each line in the file represents a test case. Each test case has the following format:
```
{"task_id": "SynbioEval/0, this is the task id number",
 "prompt": "This is the question you want to ask the model", 
 "solution": "this is the standard soltuion to the question"}
```

## Benchmarking Design
I designed 31 questions to test the models' knowledge of the SynBio domain. The questions are divided into 2 categories: Multiple choices questions and free response questions. The Multiple choices questions are designed to test the models' ability to recognize the correct answer to the question. The free response questions are in general more open-ended and designed to test the models' ability to follow the central dogma with the given DNA, RNA sequences.

In most of the biology/medicine related LLM benchmarking datasets, the question are mostly in multiple choices format. Indeed, this tests the domain knowledge of LLMs. However, to make LLM as a synthetic biology lab assistant. The ability to manipulate DNA, RNA, proteins sequences are essential and cannot be tested by multiple choice questions, as this task is open-ended in nature. 

For every model, I test their ability in both direct inference and using more advanced prompt engineering techniques : [Chain of Thoughts (CoT)](https://arxiv.org/abs/2205.11916)

Due to API availability, I only tested the models that I have access to: GPT 3.5 Turbo, GPT 4, PaLM 2 (Bison model) and Cohere

All of the models are tested under the chat scenerio, to create a easy to use interface, I used [langchain](https://www.langchain.com/) to wrap up the models and create sequencial chains to implement chain of thoughts.

## Results
| Model | MC Accuracy @ Regular| MC Accuracy @ CoT | FR Accuracy @ Regular | FR Accuracy @ CoT | Regular Accuracy | CoT Accuracy | Total Accuracy |
| ----- | --------------------- | ------------------ | --------------------- | ------------------ | ----------------- | -------------- | -------------- |
| GPT 3.5 Turbo | 0.53 | 0.28 | 0.125 | 0.1875 | 0.32| 0.26 | 0.29 |
| GPT 4 | 0.93 | 0.4 | 0.25 | 0.25| 0.65| 0.32| 0.48|
| PaLM (Bison)| 0.73| 0.53 |0.125| 0.1875 | 0.42 | 0.35 | 0.26|
| Cohere | 0.47 | 0.2 | 0.06 | 0.06 | 0.26 | 0.13| 0.13|

Here is a list of heat maps that shows the task completion status for each given model. Red meaning the model has at least got the answer correctly once whether it's under CoT or regular testing. 
![Heat Map on task completion in Chat GPT 3.5 Turbo](Figures/image-1.png)
![Heat Map on task completion in Chat GPT 4](Figures/image-2.png)
![Heat Map on task completion in PaLM](Figures/image-3.png)
![Heat Map on task completion in Cohere](Figures/image-4.png)


## Limitations
This is a non comprehensive benchmarking test suite of the ability for large language models to perform synthetic biology tasks. The models tested in the original code is also limited as I wasn't able to get access to certain API keys from certain companies.

The test suite is also limited in the number of questions it currently has. 



## Things to improve


## Author
Roselle Wang - [ruohongrosellew](https://github.com/ruohongrosellew)


## Acknowledgements and Cited Work
Some of the multiple choices questions in the test suite are derived from the Bio 1A and BIOE 10 course at the University of California, Berkeley. 