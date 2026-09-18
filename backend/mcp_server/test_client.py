import asyncio
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def main():
    print("--- Starting MCP Test Client ---")
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "backend.mcp_server.server"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("\n--- Testing list_tools() ---")
            tools = await session.list_tools()
            for t in tools.tools:
                print(f"- {t.name}: {t.description}")
                
            print("\n--- Testing tool: list_watchlist ---")
            watchlist_res = await session.call_tool("list_watchlist", {"active_only": True})
            print("Response:", watchlist_res)
            
            print("\n--- Testing tool: check_amazon_price (Fake ASIN) ---")
            fake_asin_res = await session.call_tool("check_amazon_price", {"asin": "INVALID_ASIN_123"})
            print("Response:", fake_asin_res)
            
    print("\n--- MCP Test Client Finished ---")

if __name__ == "__main__":
    asyncio.run(main())
