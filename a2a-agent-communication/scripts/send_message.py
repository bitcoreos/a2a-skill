#!/usr/bin/env python3
"""
Send A2A messages to Agent Zero with support for:
- Text messages
- File attachments
- Context tracking for conversations
- Multiple authentication methods
"""

import sys
import json
import uuid
import argparse
import base64
import asyncio
import httpx
from pathlib import Path
from typing import Optional


class A2AClient:
    """Simple A2A client for Agent Zero."""
    
    def __init__(self, base_url: str, token: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.context_id: Optional[str] = None
        self.session_file = Path.home() / ".a2a_sessions.json"
        self._load_sessions()
    
    def _load_sessions(self):
        """Load saved context IDs from file."""
        if self.session_file.exists():
            try:
                data = json.loads(self.session_file.read_text())
                self.context_id = data.get(self.base_url)
            except Exception:
                pass
    
    def _save_sessions(self):
        """Save context IDs to file."""
        data = {}
        if self.session_file.exists():
            try:
                data = json.loads(self.session_file.read_text())
            except Exception:
                pass
        data[self.base_url] = self.context_id
        self.session_file.write_text(json.dumps(data, indent=2))
    
    def _make_url(self) -> str:
        """Build A2A URL with token."""
        return f"{self.base_url}/a2a/t-{self.token}"
    
    def _encode_file(self, path: str) -> dict:
        """Encode file as base64 for attachment."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        content = file_path.read_bytes()
        return {
            "kind": "file",
            "file": {
                "name": file_path.name,
                "mimeType": "application/octet-stream",
                "bytes": base64.b64encode(content).decode()
            }
        }
    
    async def send_message(
        self,
        text: str,
        attachments: list = None,
        use_context: bool = True
    ) -> dict:
        """Send message to Agent Zero."""
        
        # Build message parts
        parts = [{"kind": "text", "text": text}]
        
        if attachments:
            for path in attachments:
                parts.append(self._encode_file(path))
        
        # Build message
        message = {
            "role": "user",
            "parts": parts,
            "kind": "message",
            "message_id": str(uuid.uuid4())
        }
        
        # Include context_id if available and requested
        if use_context and self.context_id:
            message["context_id"] = self.context_id
        
        payload = {"message": message}
        
        # Send request
        url = self._make_url()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            resp.raise_for_status()
            data = resp.json()
        
        # Update and save context_id
        new_context = data.get("result", {}).get("context_id")
        if new_context:
            self.context_id = new_context
            self._save_sessions()
        
        return data
    
    def extract_response_text(self, data: dict) -> str:
        """Extract text response from A2A result."""
        history = data.get("result", {}).get("history", [])
        if not history:
            return "(no response)"
        
        # Get last assistant message
        for msg in reversed(history):
            if msg.get("role") == "agent":
                parts = msg.get("parts", [])
                texts = [p.get("text", "") for p in parts if p.get("kind") == "text"]
                return "\n".join(texts) if texts else "(no text response)"
        
        return "(no agent response)"


def main():
    parser = argparse.ArgumentParser(description="Send A2A messages to Agent Zero")
    parser.add_argument("url", help="Agent Zero base URL")
    parser.add_argument("message", help="Message text to send")
    parser.add_argument("-f", "--file", action="append", help="File attachment (repeatable)")
    parser.add_argument("-t", "--token", required=True, help="A2A token")
    parser.add_argument("--no-context", action="store_true", help="Start fresh conversation")
    parser.add_argument("--timeout", type=int, default=60, help="Request timeout (seconds)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    client = A2AClient(args.url, args.token, args.timeout)
    
    async def run():
        try:
            print(f"📤 Sending message to {args.url}...")
            if args.file:
                print(f"   Attachments: {', '.join(args.file)}")
            
            result = await client.send_message(
                text=args.message,
                attachments=args.file,
                use_context=not args.no_context
            )
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                response_text = client.extract_response_text(result)
                print(f"\n📨 Response:")
                print(f"{response_text}")
                print(f"\n📝 Context ID: {client.context_id}")
            
            return 0
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            return 1
    
    return asyncio.run(run())


if __name__ == "__main__":
    sys.exit(main())
