import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from backend.db.session import SessionLocal
from backend.db.models import Product

async def fix_names():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "backend.mcp_server.server"]
    )
    
    db = SessionLocal()
    
    print("--- Before Fix ---")
    products = db.query(Product).order_by(Product.id).all()
    for p in products:
        print(f"ID {p.id}: {p.name} -> {p.external_id}")
        
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            watchlist_res = await session.call_tool("list_watchlist", {"active_only": False})
            
            for item in watchlist_res.content[0].text:
                # The text is actually a JSON string. We can just query db directly for the update.
                pass
                
            # Better to use the DB to iterate and MCP to fetch
            for p in products:
                title = None
                if p.source.value == "amazon":
                    res = await session.call_tool("check_amazon_price", {"asin": p.external_id})
                    import json
                    data = json.loads(res.content[0].text)
                    title = data.get("title")
                elif p.source.value == "ubuy":
                    res = await session.call_tool("check_ubuy_stock", {"product_url": p.external_id, "region": p.region})
                    import json
                    data = json.loads(res.content[0].text)
                    title = data.get("title")
                    
                if title:
                    p.name = title
                    print(f"Updated ID {p.id} name to: {title}")
                else:
                    print(f"Could not fetch title for ID {p.id}")
            
            db.commit()

    print("\n--- After Fix ---")
    for p in products:
        print(f"ID {p.id}: {p.name} -> {p.external_id}")
        
    db.close()

if __name__ == "__main__":
    asyncio.run(fix_names())
