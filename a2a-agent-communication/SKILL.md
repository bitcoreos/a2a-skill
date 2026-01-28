---
name: a2a-agent-communication
description: >
  Enables agents to communicate with Agent Zero instances via A2A protocol.
  Use when connecting to remote Agent Zero agents, sending messages with file
  attachments, managing multi-turn conversations, or coordinating multi-agent
  workflows. Supports FastA2A v0.2+ protocol with automatic context management,
  file attachments, and comprehensive error handling.
license: Apache-2.0
compatibility: >
  Requires FastA2A-compatible agents. Compatible with Agent Zero, Claude Code,
  and any FastA2A v0.2+ implementation.
metadata:
  author: bitcoreos
  version: "1.0.0"
  category: integration
  tags: [a2a, agent-zero, fasta2a, multi-agent, communication]
---

# A2A Agent Communication

This skill enables communication between agents using the FastA2A protocol, specifically designed for Agent Zero instances.

## Quick Start

### Send a simple message
```bash
# Using token URL (recommended)
curl -X POST http://agent:8080/a2a/t-YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [{"kind": "text", "text": "Hello from A2A"}]
    }
  }'
```

### Send with file attachment
```bash
# Attach a file (base64 encoded)
curl -X POST http://agent:8080/a2a/t-YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [
        {"kind": "text", "text": "Analyze this file"},
        {"kind": "file", "file": {"uri": "file:///path/to/document.pdf"}}
      ]
    }
  }'
```

### Continue conversation with context
```bash
# First message gets context_id in response
# Include it in subsequent messages to continue
```

## Authentication Methods

Agent Zero A2A supports 4 authentication methods:

### 1. Token URL (Recommended)
```
http://host:port/a2a/t-{TOKEN}/.well-known/agent.json
```

### 2. Bearer Token Header
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://host:port/a2a/.well-known/agent.json
```

### 3. X-API-KEY Header
```bash
curl -H "X-API-KEY: YOUR_TOKEN" \
  http://host:port/a2a/.well-known/agent.json
```

### 4. Query Parameter
```bash
curl "http://host:port/a2a/.well-known/agent.json?api_key=YOUR_TOKEN"
```

## Token Source

The token is derived from Agent Zero settings:
- Field: `mcp_server_token`
- Length: 16 alphanumeric characters
- Same token used for MCP server and A2A

## Message Format

### Request Structure
```json
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "Message content"},
      {"kind": "file", "file": {"uri": "file:///path/to/file"}}
    ],
    "context_id": "optional-existing-context",
    "message_id": "auto-generated-uuid"
  }
}
```

### Response Structure
```json
{
  "result": {
    "id": "task-uuid",
    "context_id": "conversation-uuid",
    "history": [
      {"role": "user", "parts": [...]},
      {"role": "agent", "parts": [{"kind": "text", "text": "Response"}]}
    ],
    "status": {"state": "completed"}
  }
}
```

## Context Management

Agent Zero handles context differently than persistent sessions:

1. **Server-side**: Creates temporary AgentContext per A2A conversation
2. **Auto-cleanup**: Context destroyed after completion/failure (like MCP)
3. **Client responsibility**: Track `context_id` for conversation continuity
4. **Context reuse**: Include `context_id` in subsequent messages to continue

## File Attachments

Supported URI schemes:
- `file://` - Local filesystem paths
- `http://` - HTTP URLs
- `https://` - HTTPS URLs

Files are passed as base64 in the `file` part structure.

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid/missing token | Check token from settings |
| `404 Not Found` | Agent card unavailable | Verify URL and server status |
| `408 Timeout` | Request timeout | Increase timeout or simplify request |
| `500 Server Error` | Processing failure | Check Agent Zero logs |

### Retry Strategy
- Exponential backoff for 5xx errors
- Immediate retry for 408 timeouts
- No retry for 401 authentication failures

## Advanced Usage

### Conversation with Context Tracking
```python
import uuid
import httpx

class A2AClient:
    def __init__(self, base_url: str, token: str):
        self.url = f"{base_url}/a2a/t-{token}"
        self.context_id = None
    
    async def send(self, message: str, attachments: list = None):
        parts = [{"kind": "text", "text": message}]
        if attachments:
            for uri in attachments:
                parts.append({"kind": "file", "file": {"uri": uri}})
        
        payload = {
            "message": {
                "role": "user",
                "parts": parts,
                "message_id": str(uuid.uuid4())
            }
        }
        if self.context_id:
            payload["message"]["context_id"] = self.context_id
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.url, json=payload)
            data = resp.json()
            self.context_id = data.get("result", {}).get("context_id")
            return data
```

### Multi-Agent Workflow
```python
# Hyperion sends to Coraline
hyperion_client = A2AClient("http://64.23.131.221:50080", TOKEN)
response = await hyperion_client.send("Research this topic")

# Process response and forward to another agent
third_party_client = A2AClient("http://third.agent:8080", OTHER_TOKEN)
await third_party_client.send(f"Hyperion found: {response}")
```

## References

- [A2A Protocol Details](references/A2A_PROTOCOL.md)
- [Agent Zero Connectivity Guide](https://github.com/agent0ai/agent-zero/blob/main/docs/connectivity.md)
- [FastA2A Specification](https://github.com/a2a-protocol/fasta2a)
