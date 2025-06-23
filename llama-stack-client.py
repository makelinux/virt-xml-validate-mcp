#!/usr/bin/env python3

print('Loading...', end='', flush=True)
import logging
import os
from llama_stack_client import RAGDocument
from llama_stack_client import Agent, LlamaStackClient
from llama_stack_client.types.tool_group import McpEndpoint
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack.distribution.library_client import LlamaStackAsLibraryClient
print('\r\033[KLoaded')

logging.getLogger("llama_stack_client._base_client").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

client = None

try:
    #client = LlamaStackClient(base_url="http://localhost:8321", timeout=300, max_retries=20)
    client = LlamaStackClient(base_url="http://localhost:8321")
    print('Connecting...', end='', flush=True)
    models = client.models.list()
    print('\r\033[K', end='', flush=True)
except:
    client = LlamaStackAsLibraryClient("ollama")
    print('\r\033[K', end='', flush=True)
    client.initialize()
    models = client.models.list()
    print('Using library')

tools=[]

# llama-stack-client toolgroups register mcp::virt --provider-id model-context-protocol --mcp-endpoint http://0.0.0.0:3002/sse --args
client.toolgroups.register(
    toolgroup_id="mcp::virt",
    provider_id="model-context-protocol",
    #mcp_endpoint=McpEndpoint(uri="http://0.0.0.0:3002/sse"),
    mcp_endpoint=McpEndpoint(uri="http://0.0.0.0:3002/sse"),
)
tools+=["mcp::virt"]

def rag(sources):
    embedding_model_id = (
        em := next(m for m in models if m.model_type == "embedding")
    ).identifier

    documents = []
    for i, s in enumerate(sources):
        print("rag_tool> Ingesting document:", s)
        documents += [ RAGDocument(document_id=f"doc-{i}",
                                   content=s,
                                   mime_type="text/plain",
                                   metadata={},
                                   )
                      ]

    vector_db_id = "my_demo_vector_db"
    _ = client.vector_dbs.register(
        vector_db_id=vector_db_id,
        embedding_model=embedding_model_id,
        embedding_dimension= em.metadata["embedding_dimension"],
        provider_id="faiss",
    )
    client.tool_runtime.rag_tool.insert(
        documents=documents,
        vector_db_id=vector_db_id,
        chunk_size_in_tokens=512,
    )
    global tools
    tools+=[{ "name": "builtin::rag/knowledge_search", "args": {"vector_db_ids": [vector_db_id]}}]

    if True:
        results = client.tool_runtime.rag_tool.query(
            vector_db_ids=[vector_db_id],
            #content="How objects in the libvirt API are configured?",
            content="What are the key topics in the documents?",
            )
        print(results)

rag(["https://libvirt.org/format.html"])#, "https://libvirt.org/formatdomain.html"])

agent = Agent(
    client,
    model=os.getenv('INFERENCE_MODEL', 'llama3.2:3b'),
    instructions="""You are a helpful assistant that can use tools to answer questions.""",
    tools=tools
)

user_prompts = [
       "Validate libvirt XML: '<domain type='kvm'> <name>test</name> </domain>'",
       "Validate libvirt XML: '<domain type='kvm'>  </domain>'",
        ]

session_id = agent.create_session("demo-session")

for prompt in user_prompts:
    print()
    print(f"User> {prompt}\n")
    response = agent.create_turn(messages=[{"role": "user", "content": prompt}], session_id=session_id)
    for log in EventLogger().log(response):
        log.print()
