#!/usr/bin/env python3

import os
import json
import sys
import numpy as np
import time
from datetime import timedelta
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import BucketNotFoundException, ScopeNotFoundException, InternalServerFailureException
from couchbase.exceptions import UnAmbiguousTimeoutException, AuthenticationException
from langchain_couchbase import CouchbaseVectorStore
from langchain_couchbase.cache import CouchbaseSemanticCache
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.globals import set_llm_cache, get_llm_cache
from langchain_core.caches import RETURN_VAL_TYPE, BaseCache
from langchain_openai import OpenAI
from langchain_core.load.dump import dumps
import asyncio
from concurrent.futures import ThreadPoolExecutor

CB_HOSTNAME = os.getenv("CB_HOSTNAME")
CB_USERNAME = os.getenv("CB_USERNAME")
CB_PASSWORD = os.getenv("CB_PASSWORD")
CB_BUCKET = os.getenv("CB_BUCKET")
CB_SCOPE = os.getenv("CB_SCOPE")
CB_COLLECTION = os.getenv("CB_COLLECTION")
CB_SEARCHINDEX = os.getenv("CB_SEARCHINDEX")

def seed_cache(cache, prompt, answer):

    params = llm.dict()
    params["stop"] = None
    llm_string = str(sorted([(k,v) for k, v in params.items()]))

    cache.update(
        prompt,
        llm_string,
        [{
            "lc": 1,
            "type": "constructor",
            "id": ["langchain", "schema", "output", "Generation"],
            "kwargs": {
                "text": answer,
                "generation_info": {
                    "finish_reason": "stop",
                    "logprobs": None
                },
                "type": "Generation"
            }
        }]
    )

pa = PasswordAuthenticator(CB_USERNAME, CB_PASSWORD)
# cluster = Cluster("couchbase://" + CB_HOSTNAME, ClusterOptions(pa))
cluster = Cluster("couchbases://" + CB_HOSTNAME + "/?ssl=no_verify", ClusterOptions(pa))
cluster.wait_until_ready(timedelta(seconds=5))

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print(f"Missing required environment variable: OPENAI_API_KEY")
    sys.exit(1)

client = OpenAI(api_key=openai_api_key)

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
llm = OpenAI(model_name="gpt-3.5-turbo-instruct", n=2, best_of=2)

cache = CouchbaseSemanticCache(
    cluster=cluster,
    embedding=embeddings,
    bucket_name=CB_BUCKET,
    scope_name=CB_SCOPE,
    collection_name=CB_COLLECTION,
    index_name=CB_SEARCHINDEX,
    score_threshold=0.8,
)

cache.clear() # curious what this does under the hood WRT couchbase
set_llm_cache(cache)

# Array of prompts and answers
prompts_and_answers = [
    ("Who is the world's greatest coder?", "Jon Strabla, just joking!"),
    ("How much is to call mars?", "Calling Mars by radio can costs $1,000 USD per minute at NASA."),
    ("Why is the moon made of cheese?", "Because if it was made of water it would evaporate into space."),
    ("Who is the 2024 Republican VP Pick in the U.S.", "JD Vance."),
    ("Who is the 2024 Democratic VP Pick in the U.S.", "Kamala Harris."),
    ("What was the S&P 500 at on 2024-07-18", "It opened at $5,608.56 and closed at $5,538.18 (with a High of $5,614.05 and a Low of $5,537.13)")
]

# Loop through the array and seed the cache
for prompt, answer in prompts_and_answers:
    seed_cache(cache, prompt, answer)

if False:
    for _ in range(5):
        messages = [
            {"role": "system", "content": "You are a knowledgeable assistant."},
            {"role": "user", "content": "Tell me a joke"}
        ]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-3.5-turbo",
        )
        response_content = chat_completion.choices[0].message.content
        print(response_content)

print()
if True:
    print("=============================================")
    print("Let's search for something NOT in the cache")
    print("=============================================")
    print()
    for i in range(2):
        question = "How long do dogs live?"
        start_time = time.time()
        resp = llm.invoke(question)
        end_time = time.time()
        print("Question :", question.strip())
        print("Answer   :", resp.strip())
        elapsed_time = end_time - start_time
        print(f"Test {i}. Execution time: {elapsed_time:.4f} seconds")
        print()

    print("=============================================")
    print("Let's search for something 'similar' to something in the cache but not in it")
    print("=============================================")
    print()
    question = "How long do canines live?"
    start_time = time.time()
    resp = llm.invoke(question)
    end_time = time.time()
    print("Question :", question.strip())
    print("Answer   :", resp.strip())
    elapsed_time = end_time - start_time
    print(f"Test 1. Execution time: {elapsed_time:.4f} seconds")
    print()

    question = "How long is the lifespan of a dog?"
    start_time = time.time()
    resp = llm.invoke(question)
    end_time = time.time()
    print("Question :", question.strip())
    print("Answer   :", resp.strip())
    elapsed_time = end_time - start_time
    print(f"Test 1. Execution time: {elapsed_time:.4f} seconds")
    print()

if True:
    print("=============================================")
    print("Let's search for all items seeded into the cache")
    print("=============================================")
    print()
    i = 0
    for question, _ in prompts_and_answers:
        i += 1
        start_time = time.time()
        resp = llm.invoke(question)
        end_time = time.time()
        print("Question :", question.strip())
        print("Answer   :", resp.strip())
        elapsed_time = end_time - start_time
        print(f"Test {i}. Execution time: {elapsed_time:.4f} seconds")
        print()

if True:
    loops = 100
    print("=============================================")
    print(f"Let's search for something seeded into the cache {loops} times sequentially")
    print("=============================================")
    print()
    question = "How much is to call mars?"
    print("Question :", question.strip())
    start_time = time.time()
    for i in range(loops):
        resp = llm.invoke(question)
    end_time = time.time()
    print("Answer   :", resp.strip())
    elapsed_time = end_time - start_time
    rps = loops / elapsed_time
    print(f"Tests 1..{loops} Execution time for {loops} reqs: {elapsed_time:.4f} seconds, reqs/sec: {rps:.4f}")
    print()

# Assuming llm.invoke is synchronous, we wrap it to make it async
def invoke_sync(question):
    return llm.invoke(question)

async def invoke_async(question, executor):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, invoke_sync, question)

async def async_test():
    loops = 100
    print("=============================================")
    print(f"Let's search for something seeded into the cache {loops} times via async calls")
    print("=============================================")
    print()
    question = "How much is to call mars?"
    print("Question :", question.strip())

    start_time = time.time()
    # Use ThreadPoolExecutor for running synchronous code in async context
    with ThreadPoolExecutor() as executor:
        tasks = [invoke_async(question, executor) for _ in range(loops)]
        responses = await asyncio.gather(*tasks)

    end_time = time.time()
    elapsed_time = end_time - start_time
    rps = loops / elapsed_time

    # Print the last response for consistency with original code
    print("Answer   :", responses[-1].strip())
    print(f"Tests 1..{loops} Execution time for {loops} reqs: {elapsed_time:.4f} seconds, reqs/sec: {rps:.4f}")
    print()

# Run the async main function
asyncio.run(async_test())

