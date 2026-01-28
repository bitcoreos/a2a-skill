# A2A Agent Communication Skill

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A comprehensive skill for enabling agent-to-agent communication via the FastA2A protocol, specifically designed for [Agent Zero](https://github.com/agent0ai/agent-zero) instances.

## 🎯 What This Skill Does

This skill enables agents to:
- ✅ Communicate with remote Agent Zero instances via A2A protocol
- ✅ Send messages with file attachments
- ✅ Manage multi-turn conversations with context tracking
- ✅ Coordinate multi-agent workflows
- ✅ Handle authentication using multiple methods

## 📦 Installation

### For Claude Code
```bash
/plugin install a2a-agent-communication@bitcoreos
```

### For Claude.ai
1. Navigate to Settings → Skills → Add Skill
2. Upload the `a2a-agent-communication` folder

### For Agent Zero
Copy the skill folder to your Agent Zero skills directory:
```bash
cp -r a2a-agent-communication /path/to/agent-zero/skills/
```

## 🚀 Quick Start

### 1. Validate Connection
```bash
cd a2a-agent-communication/scripts
python validate_connection.py http://agent:8080 --token YOUR_TOKEN
```

### 2. Send a Message
```bash
python send_message.py http://agent:8080 "Hello from A2A!" -t YOUR_TOKEN
```

### 3. Send with File Attachment
```bash
python send_message.py http://agent:8080 "Analyze this report" -t YOUR_TOKEN -f report.pdf
```

### 4. Continue Conversation
```bash
# First message creates context
python send_message.py http://agent:8080 "Initial question" -t YOUR_TOKEN

# Follow-up uses saved context automatically
python send_message.py http://agent:8080 "Follow-up question" -t YOUR_TOKEN
```

## 🔑 Authentication

Agent Zero A2A requires a token for authentication. Obtain your token from:
- Agent Zero Settings → MCP Server → MCP Server Token
- Environment variable: `MCP_SERVER_TOKEN`
- 16-character alphanumeric string

Supported authentication methods:
1. **Token URL**: `http://host/a2a/t-{TOKEN}`
2. **Bearer**: `Authorization: Bearer {TOKEN}`
3. **API Key**: `X-API-KEY: {TOKEN}`
4. **Query**: `?api_key={TOKEN}`

## 📋 Skill Contents

```
a2a-agent-communication/
├── SKILL.md                    # Main skill guide
├── scripts/
│   ├── validate_connection.py  # Test A2A connectivity
│   └── send_message.py         # Send messages with attachments
└── references/
    └── A2A_PROTOCOL.md         # FastA2A v0.2+ specification
```

## 🌐 Network Architecture

This skill enables communication in multi-agent setups:

```
┌─────────────────┐      A2A      ┌─────────────────┐
│   Hyperion      │ ◄────────────► │    Coraline     │
│  (Agent Zero)   │   Protocol     │  (Agent Zero)   │
│ 64.227.106.173  │                │ 64.23.131.221   │
└─────────────────┘                └─────────────────┘
```

## 🔧 Advanced Usage

### Direct API Calls

```bash
# Send message with curl
curl -X POST http://agent:8080/a2a/t-YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [{"kind": "text", "text": "Hello"}]
    }
  }'
```

### Python Integration

```python
import asyncio
from scripts.send_message import A2AClient

async def main():
    client = A2AClient("http://agent:8080", "YOUR_TOKEN")
    
    # Send message
    result = await client.send_message("Hello!")
    print(client.extract_response_text(result))
    
    # Continue conversation
    result2 = await client.send_message("Follow-up question")
    print(client.extract_response_text(result2))

asyncio.run(main())
```

## 📚 Documentation

- [SKILL.md](a2a-agent-communication/SKILL.md) - Complete usage guide
- [A2A_PROTOCOL.md](a2a-agent-communication/references/A2A_PROTOCOL.md) - Protocol specification
- [Agent Zero Connectivity](https://github.com/agent0ai/agent-zero/blob/main/docs/connectivity.md) - Official docs

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

Apache-2.0 - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Agent Zero](https://github.com/agent0ai/agent-zero) - The autonomous agent framework
- [FastA2A](https://github.com/a2a-protocol/fasta2a) - Agent-to-agent protocol
- [Anthropic Skills](https://github.com/anthropics/skills) - Skills framework inspiration

---

**Created by**: [bitcoreos](https://github.com/bitcoreos)  
**Version**: 1.0.0  
**Last Updated**: 2026-01-28
