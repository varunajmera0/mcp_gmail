import asyncio
import json
from fastmcp.client import Client
from fastmcp.client.transports import SSETransport
from mcp_gmail.config import settings

async def main():
    # Build the SSE endpoint URL from configuration
    url = f"{settings.BASE_URL_PROTOCOL}://{settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}/{settings.MCP_TRANSPORT}"
    async with Client(SSETransport(url)) as client:
        # List up to 5 messages with attachments
        resp = await client.call_tool(
            "gmail://messages",
            {"q": "has:attachment", "max_results": 1}
        )
        msgs = json.loads(resp[0].text)
        if not msgs:
            print("No attachments found.")
            return

        # Process each message
        for m in msgs:
            mid = m["id"]
            print(f"Msg {mid} → downloading attachments...")
            dl = await client.call_tool(
                "gmail://attachments",
                {"msg_id": mid}
            )
            res = json.loads(dl[0].text)
            print("Saved:", res.get("saved"))
            if res.get("protected"):
                pwd = input("Enter password for protected attachments: ")
                dl2 = await client.call_tool(
                    "gmail://attachments",
                    {"msg_id": mid, "password": pwd}
                )
                print("Saved after decrypt:", json.loads(dl2[0].text).get("saved"))

if __name__ == '__main__':
    asyncio.run(main())