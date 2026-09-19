import asyncio
import logging
from dotenv import load_dotenv
load_dotenv()
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from backend.agent.graph import create_inventory_graph

logger = logging.getLogger(__name__)

async def async_run_agent():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "backend.mcp_server.server"]
    )
    logger.info("Starting MCP Client Session...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            logger.info("Loading MCP Tools via langchain-mcp-adapters...")
            tools = await load_mcp_tools(session)
            tools_dict = {t.name: t for t in tools}
            logger.info(f"Tools available: {list(tools_dict.keys())}")
            
            logger.info("Compiling LangGraph Agent...")
            graph = create_inventory_graph(tools_dict)
            
            logger.info("Starting Graph Execution...")
            result = await graph.ainvoke({"product_results": []})
            
            logger.info("=== Agent Run Complete ===")
            logger.info(f"Run ID: {result.get('run_id')}")
            logger.info("Summary:\n" + str(result.get('summary')))
            return result

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    await async_run_agent()

if __name__ == "__main__":
    asyncio.run(main())
