## Basic Couchbase RAG with Semantic Cache Demo, Langchain, and OpenAI

This is a demo app built to highlight basic functionality of vector search of Couchbase to utilize OpenAI embeddings for semantic search to implement RAG with caching.
Once your environment variables are setup and your server has the right resources. 

The demo will run for both self-managed OnPrem 7.6+ Couchbase deployments and also clould based 7.6+ Capella deployments.

If you don't have the time to run the demo you can just download and watch the 4 minute video: [easy-vector-langchain-demo_1920x1080.mp4](https://github.com/jon-strabala/easy-vector-langchain-demo/blob/main/easy-vector-langchain-demo_1920x1080.mp4) 

### Prerequisites 

You will need a database user with login credentials to your Couchbase cluster and an OpenAI API bearer key for this Linux demo

You will probably want to create and activate a virtual environment using the standard library's virtual environment tool, *venv*, and install local python packages.

- https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

Quick tips on Python virtual environments (please folow this unless you are an expert). 

- Create and activate a virtual environment in a new empty demo directory<br><br>
`mkdir MYDEMO`<br>
`cd MYDEMO`<br>
`python3 -m venv .venv`<br>
`source .venv/bin/activate`

- The above works for *bash* or *zsh*, however you would use `. .venv/bin/activate` if you are using *sh*

- Then, when all done with this demo, you can deactivate it.<br><br>
`deactivate`

- Just in case you typed 'deactive' (you do this deactive when you're done with the full demo) - just run the source command again to reactivate the virtual Python environment:<br><br>
`source .venv/bin/activate`

- The above works for *bash* or *zsh*, however you would use `. .venv/bin/activate` if you are using *sh*

- Now download this git repo and cd into it.<br><br>
`git clone https://github.com/jon-strabala/easy-semantic-cache-demo.git`<br>
`cd easy-semantic-cache-demo`

### How does this demo work?

It loads ten (10) simple words into a Couchbase collection.

It executes three (3) canned queries against the Couchbase collection containing your vector embeddings.

For each question, you will three ordered answers from your vector search

### How to Run

- Install dependencies

  `pip install -r requirements.txt`

- Copy the template environment template

  `cp _setup.tmpl _setup`

- Required environment variables that you must configure in _setup
  ```
  export CB_HOSTNAME="<the hostname or IP address of your Couchbase server>" 
  export CB_FTSHOSTNAME="<the hostname or IP address of a node running Search in your Couchbase cluster>" 
  export CB_USERNAME="<username_for_couchbase_cluster>" 
  export CB_PASSWORD="<password_for_couchbase_cluster>"
  export OPENAI_API_KEY="<open_ai_api_key>"
  ```
  
- Note CB_HOSTNAME might be different than CB_FTSHOSTNAME if your services are distributed (these are the same on a single node cluster).
  - The evar CB_HOSTNAME is typically an IP in your cluster (or the Capella CONNECT hostname) running the data service (or KV) for the Python SDK to connect to couchbases://${CB_HOSTNAME}. 
  - The evar CB_FTSHOSTNAME is set to a node running the search service (or fts) for a curl like connection to https://${CB_FTSHOSTNAME}:18094 used for index creation.
  - This example always uses and assumes secure connections to your couchbase instance, you should verify your firewall will pass at least 18091 (Management port), 18094 (Search service), 11210 / 11207 (Data service)

- Optional environment variables that you may alter in _setup

  ```
  export CB_BUCKET=vectordemos
  export CB_SCOPE=langchain
  export CB_COLLECTION=semantic-cache
  export CB_SEARCHINDEX="semantic-cache-index"
  ```

- Source the _setup file (we assume a bash shell) to configure your environment variables

  `source _setup`

- The above works for *bash* or *zsh*, however you would use `. _setup` if you are using *sh*

- If needed set the executable bits on various files via chmod for the following:

  `chmod +x basic_couchbase_langchain.py  check_couchbase.sh  check_openai.py  setup.py`

- Verify connectivity and authentication to your Couchbase server

  `./check_couchbase.sh`

- Verify connectivity and authentication to OpenAI

  `./check_openai.py`

- Setup the Couchbase infrastructure (bucket, scope, collection and a search vector index) via the bash script

  `./setup.py`

- Run the first application a simple in memory key value store (this is exact search) you canskp this step if you want.

  `./simple_memory_cache_test.py`

- Look at the code above to see how it works.

- Run the second application a simple RAG application that uses COuchbase Vector search and a Semantic Cache (this can avoid LLM calls for similar answers)

  `./simple_couchbase_semantic_cache_test.py`

- Look at the code above to see how it works.

- Finished

  When you are all done with this demo, you should deactivate the python virtual environment (you can always reactivate it later).<br><br>
  `deactivate`
