#!/usr/bin/env python3

print('Loading...', end='', flush=True)
import logging
import os
from llama_stack_client import Agent, LlamaStackClient
from llama_stack_client.types.tool_group import McpEndpoint
from llama_stack_client.lib.agents.event_logger import EventLogger
print('\r\033[KLoaded')

logging.getLogger("llama_stack_client._base_client").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

client = LlamaStackClient(base_url="http://localhost:8321", max_retries=20)
print('Connecting...', end='', flush=True)
models = client.models.list()
print('\r\033[K', end='', flush=True)
client.toolgroups.register(
    toolgroup_id="mcp::virt",
    provider_id="model-context-protocol",
    #mcp_endpoint=McpEndpoint(uri="http://0.0.0.0:3002/sse"),
    mcp_endpoint=McpEndpoint(uri="http://0.0.0.0:3002/sse"),
)

agent = Agent(
    client,
    model=os.getenv('INFERENCE_MODEL', 'llama3.2:3b'),
    instructions="""You are a helpful assistant that can use tools to answer questions.""",
    tools=["mcp::virt"]
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
