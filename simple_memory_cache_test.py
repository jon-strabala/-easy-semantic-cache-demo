#!/usr/bin/env python3

import os
import json
import sys
import numpy as np
import time
from datetime import timedelta

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.globals import set_llm_cache, get_llm_cache
from langchain_core.caches import RETURN_VAL_TYPE, BaseCache
from langchain_openai import OpenAI
from langchain_core.load.dump import dumps
from langchain_community.cache import InMemoryCache

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Missing required environment variable: OPENAI_API_KEY")
    sys.exit(1)

client = OpenAI(api_key=openai_api_key)

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
llm = OpenAI(model_name="gpt-3.5-turbo-instruct", n=2, best_of=2)

set_llm_cache(InMemoryCache())

print("\nThe InMemoryCache from langchain_community.cache does not inherently perform similarity search.")
print("It is a basic in-memory cache implementation that stores key-value pairs, where keys are usually")
print("prompts and values are their corresponding outputs. It is primarily used to cache the results of")
print("queries to avoid redundant computations or API calls.\n")

print("=============================================")
print("Let's search for something NOT in the cache")
print("=============================================")
print()
for i in range(2):
    question = "How long do dogs live?"
    start_time = time.time()
    resp = llm.invoke(question)
    end_time = time.time()
    print("Question:", question.strip())
    print("Answer:", resp.strip())
    elapsed_time = end_time - start_time
    print(f"Test {i + 1}. Execution time: {elapsed_time:.4f} seconds")
    print()

print("=============================================")
print("Let's search for something 'similar' to something in the cache but not in it")
print("this won't speed up anything as the cache is only a basic key value store")
print("=============================================")
print()
question = "How long do canines live?"
start_time = time.time()
resp = llm.invoke(question)
end_time = time.time()
print("Question:", question.strip())
print("Answer:", resp.strip())
elapsed_time = end_time - start_time
print(f"Test 1. Execution time: {elapsed_time:.4f} seconds")
print()

question = "How long is the lifespan of a dog?"
start_time = time.time()
resp = llm.invoke(question)
end_time = time.time()
print("Question:", question.strip())
print("Answer:", resp.strip())
elapsed_time = end_time - start_time
print(f"Test 2. Execution time: {elapsed_time:.4f} seconds")
print()

loops = 100
print("=============================================")
print(f"Let's search for something cached {loops} times sequentially")
print("=============================================")
print()
question = "How long do canines live?"
print("Question:", question.strip())
start_time = time.time()
for i in range(loops):
    resp = llm.invoke(question)
end_time = time.time()
print("Answer:", resp.strip())
elapsed_time = end_time - start_time
rps = loops / elapsed_time
print(f"Test 1..{loops} Execution time for {loops} reqs: {elapsed_time:.4f} seconds ({rps:.2f} requests per second)")
print()

