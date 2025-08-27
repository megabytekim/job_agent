"""
Simple tester for an A2A agent deployed on Google Cloud Run.

Usage:
  - Without auth (public service):
      python test_cloud_run.py --url https://your-service-url
  - With automatic IAM token if needed:
      python test_cloud_run.py --url https://your-service-url

The script will try unauthenticated first. If it receives 401/403, it will
fetch an identity token using `gcloud auth print-identity-token` and retry.
"""

import argparse
import asyncio
import json
import subprocess
import sys
import uuid
from typing import Optional

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest


def get_identity_token() -> Optional[str]:
    """Return an Identity Token from gcloud, or None if unavailable."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-identity-token"],
            check=True,
            capture_output=True,
            text=True,
        )
        token = result.stdout.strip()
        return token if token else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def create_httpx_client(identity_token: Optional[str] = None) -> httpx.AsyncClient:
    headers = {}
    if identity_token:
        headers["Authorization"] = f"Bearer {identity_token}"
    return httpx.AsyncClient(timeout=30, headers=headers)


async def resolve_agent_card(base_url: str) -> tuple[httpx.AsyncClient, object]:
    """Resolve the agent card, attempting unauthenticated then with IAM token."""
    # Try without token
    client = create_httpx_client()
    resolver = A2ACardResolver(base_url=base_url, httpx_client=client)
    try:
        card = await resolver.get_agent_card()
        return client, card
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response is not None else None
        # Retry with Identity Token on 401/403
        if status in {401, 403}:
            await client.aclose()
            token = get_identity_token()
            if not token:
                raise RuntimeError(
                    "Service requires authentication but no identity token is available. "
                    "Run 'gcloud auth login' and retry."
                ) from exc
            client = create_httpx_client(identity_token=token)
            resolver = A2ACardResolver(base_url=base_url, httpx_client=client)
            card = await resolver.get_agent_card()
            return client, card
        raise


async def send_test_message(base_url: str, user_text: str) -> None:
    client, card = await resolve_agent_card(base_url)

    try:
        # Build A2A client against the card's advertised URL
        a2a_client = A2AClient(client, card, url=card.url)

        session_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())

        payload = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": user_text}],
                "messageId": message_id,
                "contextId": session_id,
            }
        }

        request = SendMessageRequest(
            id=message_id, params=MessageSendParams.model_validate(payload)
        )
        # Some a2a-sdk versions expect a positional argument rather than a named 'message_request'.
        response = await a2a_client.send_message(request)
        print(json.dumps(response.model_dump(exclude_none=True), indent=2, ensure_ascii=False))
    finally:
        await client.aclose()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test a Cloud Run A2A agent")
    parser.add_argument(
        "--url",
        required=False,
        default="https://job-agent-113466776893.us-central1.run.app",
        help="Base URL of the Cloud Run service (e.g. https://...a.run.app)",
    )
    parser.add_argument(
        "--text",
        required=False,
        default="I want to order 1 Margherita Pizza. Please confirm the total price.",
        help="Test user message to send",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_url = args.url.rstrip("/")
    try:
        asyncio.run(send_test_message(base_url, args.text))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


