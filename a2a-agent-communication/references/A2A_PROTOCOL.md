# FastA2A Protocol v0.2+ Reference

Complete protocol specification for Agent-to-Agent communication.

## Overview

FastA2A is a lightweight protocol for agent communication based on HTTP with JSON payloads. Agent Zero implements FastA2A v0.2+ with extensions.

## Authentication

Agent Zero requires authentication via one of:

1. **Token URL**: Path-based token `/a2a/t-{TOKEN}`
2. **Bearer Token**: `Authorization: Bearer {TOKEN}` header
3. **API Key**: `X-API-KEY: {TOKEN}` header  
4. **Query Parameter**: `?api_key={TOKEN}`

The token is a 16-character alphanumeric string from Agent Zero settings (`mcp_server_token`).

## Agent Card

Discovery endpoint for agent capabilities.

### Request
```http
GET /.well-known/agent.json
```

### Response
```json
{
  "name": "Agent Zero",
  "description": "Autonomous agent framework",
  "url": "http://host:port/a2a/t-{TOKEN}",
  "version": "1.0.0",
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "authentication": {
    "schemes": ["bearer", "apiKey"]
  },
  "defaultInputModes": ["text/plain", "text/json"],
  "defaultOutputModes": ["text/plain", "text/json"],
  "skills": [...]
}
```

## Message Sending

### Endpoint
```http
POST /a2a/t-{TOKEN}
```

### Request Body
```json
{
  "message": {
    "role": "user",
    "parts": [
      {"kind": "text", "text": "Hello"},
      {"kind": "file", "file": {"uri": "file:///path"}}
    ],
    "context_id": "optional-context-uuid",
    "message_id": "message-uuid"
  }
}
```

### Part Types

| Kind | Fields | Description |
|------|--------|-------------|
| `text` | `text` | Plain text content |
| `file` | `file.uri` or `file.bytes` | File attachment |

### Response
```json
{
  "result": {
    "id": "task-uuid",
    "context_id": "conversation-uuid",
    "status": {"state": "completed"},
    "history": [
      {"role": "user", "parts": [...]},
      {"role": "agent", "parts": [{"kind": "text", "text": "..."}]}
    ]
  }
}
```

## Status States

- `submitted` - Task received
- `working` - Processing in progress
- `input-required` - Waiting for user input
- `completed` - Successfully finished
- `failed` - Error occurred
- `canceled` - Task canceled

## Context Management

Agent Zero creates a temporary AgentContext for each A2A conversation:

1. Context is created when first message received
2. Auto-destroyed after completion/failure
3. Context_id for continuity must be tracked client-side
4. No persistent server-side session storage

## Error Codes

| HTTP | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid JSON) |
| 401 | Unauthorized (invalid token) |
| 404 | Agent card not found |
| 408 | Request timeout |
| 500 | Server error |

## References

- [Agent Zero Connectivity](https://github.com/agent0ai/agent-zero/blob/main/docs/connectivity.md)
- [FastA2A Library](https://github.com/a2a-protocol/fasta2a)
