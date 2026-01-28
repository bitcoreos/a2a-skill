#!/usr/bin/env python3
"""
Validate A2A connectivity to an Agent Zero instance.
Tests all 4 authentication methods and reports results.
"""

import sys
import argparse
import httpx
import asyncio
from urllib.parse import urljoin, urlparse


async def test_agent_card(url: str, headers: dict = None, description: str = "") -> bool:
    """Test retrieving agent card from A2A endpoint."""
    agent_json_url = urljoin(url.rstrip('/') + '/', '.well-known/agent.json')
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(agent_json_url, headers=headers or {})
            if resp.status_code == 200:
                data = resp.json()
                print(f"  ✅ {description}")
                print(f"     Agent: {data.get('name', 'Unknown')}")
                print(f"     Description: {data.get('description', 'No description')[:60]}...")
                return True
            else:
                print(f"  ❌ {description}: HTTP {resp.status_code}")
                return False
    except Exception as e:
        print(f"  ❌ {description}: {e}")
        return False


async def validate_connection(base_url: str, token: str = None):
    """Test all authentication methods."""
    print(f"\n🔍 Validating A2A connection to: {base_url}")
    print("=" * 60)
    
    results = []
    
    # Method 1: Token URL (if provided)
    if token:
        url = f"{base_url}/a2a/t-{token}"
        ok = await test_agent_card(url, description="Token URL method")
        results.append(("Token URL", ok))
    
    # Method 2: Bearer token
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{base_url}/a2a"
        ok = await test_agent_card(url, headers=headers, description="Bearer token")
        results.append(("Bearer", ok))
    
    # Method 3: X-API-KEY header
    if token:
        headers = {"X-API-KEY": token}
        url = f"{base_url}/a2a"
        ok = await test_agent_card(url, headers=headers, description="X-API-KEY header")
        results.append(("X-API-KEY", ok))
    
    # Method 4: Query parameter
    if token:
        url = f"{base_url}/a2a/.well-known/agent.json?api_key={token}"
        ok = await test_agent_card(url, description="Query parameter")
        results.append(("Query param", ok))
    
    # Summary
    print("\n📊 Results Summary")
    print("-" * 40)
    passed = sum(1 for _, ok in results if ok)
    for method, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {method}")
    print(f"\n{passed}/{len(results)} methods working")
    
    return passed > 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate A2A connectivity to Agent Zero"
    )
    parser.add_argument("url", help="Agent Zero base URL (e.g., http://localhost:8080)")
    parser.add_argument("--token", help="A2A token (16-char alphanumeric)")
    parser.add_argument("--api-key", dest="token", help="Alias for --token")
    
    args = parser.parse_args()
    
    # Auto-detect token from URL if present
    token = args.token
    if not token and "/a2a/t-" in args.url:
        parsed = urlparse(args.url)
        if parsed.path.startswith("/a2a/t-"):
            token = parsed.path.replace("/a2a/t-", "").rstrip("/")
            print(f"🔑 Auto-detected token from URL: {token}")
    
    result = asyncio.run(validate_connection(args.url, token))
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
