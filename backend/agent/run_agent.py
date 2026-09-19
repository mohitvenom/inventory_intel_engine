import asyncio
from dotenv import load_dotenv
load_dotenv()
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from backend.agent.graph import create_inventory_graph

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "backend.mcp_server.server"]
    )
    print("Starting MCP Client Session...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("Loading MCP Tools via langchain-mcp-adapters...")
            tools = await load_mcp_tools(session)
            tools_dict = {t.name: t for t in tools}
            print("Tools available:", list(tools_dict.keys()))
            
            print("Compiling LangGraph Agent...")
            graph = create_inventory_graph(tools_dict)
            
            print("Starting Graph Execution...")
            result = await graph.ainvoke({"product_results": []})
            
            print("\n=== Agent Run Complete ===")
            print("Run ID:", result.get("run_id"))
            print("Summary:")
            print(result.get("summary"))

if __name__ == "__main__":
    asyncio.run(main())
