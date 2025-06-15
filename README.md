# virt-xml-validate MCP

In the first terminal start ollama and llama-stack:

```shell

export INFERENCE_MODEL=llama3.2:3b
echo hi | ollama run $INFERENCE_MODEL --keepalive 1h

uv run --with llama-stack llama stack build --template ollama --image-type venv --image-name ~/my-ollama-llama-stack --run
```

In the second terminal start MCP server:

```shell
./mcp_server.py
```

In the third terminal start MCP client based on llama-stack:

```shell
./llama-stack-client.py
```

# mcp-server template

MCP (ModelContextProvider) server template

---

## Building locally

To build the container image locally using Podman, run:

```sh
podman build -t mcp-server-template:latest .
```

This will create a local image named `mcp-server-template:latest` that you can use to run the server.

## Running with Podman or Docker

Example configuration for running with Podman:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "API_BASE_URL",
        "-e", "API_KEY",
        "-e", "MCP_TRANSPORT",
        "localhost/mcp-server-template:latest"
      ],
      "env": {
        "API_BASE_URL": "https://api.example.com",
        "API_KEY": "REDACTED",
        "MCP_TRANSPORT": "sse"
      }
    }
  }
}
```
