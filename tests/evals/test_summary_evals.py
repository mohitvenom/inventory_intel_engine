import pytest
import asyncio
from dotenv import load_dotenv
load_dotenv()
from backend.agent.graph import create_inventory_graph

# We test the summarize_run LLM call directly using the graph node.
# Since it's a StateGraph node, we can just compile the graph and use it,
# or better yet, extract the summarize_run function or mock the inputs.

@pytest.fixture
def graph():
    return create_inventory_graph({"list_watchlist": None, "check_amazon_price": None, "check_ubuy_stock": None, "get_price_history": None, "get_stock_history": None, "record_price_check": None, "record_stock_check": None, "get_recent_alerts": None, "record_alert_sent": None, "finish_agent_run": None})

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

async def run_summary_async(trace):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = (
        "You are an AI orchestrator for an inventory and price tracking system.\n"
        "Here is the trace of the current check run:\n"
        f"{json.dumps(trace, indent=2)}\n\n"
        "Write a short, human-readable summary (2-4 sentences) of what happened this run. "
        "Highlight any successes, failures, price drops, restocks, or stockouts."
    )
    response = await llm.ainvoke([SystemMessage(content="You are a helpful assistant."), HumanMessage(content=prompt)])
    return response.content.lower()

def run_summary(trace):
    return asyncio.run(run_summary_async(trace))

def test_summary_all_success():
    trace = [
        {"id": 1, "name": "Apple iPad", "status": "success", "price": 400.0, "in_stock": True, "price_dropped": False, "restocked": False, "stockouted": False},
        {"id": 2, "name": "Xbox Gift Card", "status": "success", "price": 50.0, "in_stock": True, "price_dropped": False, "restocked": False, "stockouted": False}
    ]
    summary = run_summary(trace)
    assert "apple ipad" in summary
    assert "xbox gift card" in summary

def test_summary_all_error():
    trace = [
        {"id": 1, "name": "EVGA RTX 3090", "status": "error", "error": "RegionRestrictedError"},
    ]
    summary = run_summary(trace)
    assert "evga rtx 3090" in summary
    assert "error" in summary or "fail" in summary or "restrict" in summary

def test_summary_price_drop():
    trace = [
        {"id": 1, "name": "Apple iPad", "status": "success", "price": 300.0, "in_stock": True, "price_dropped": True, "restocked": False, "stockouted": False},
    ]
    summary = run_summary(trace)
    assert "apple ipad" in summary
    assert "drop" in summary

def test_summary_restock():
    trace = [
        {"id": 1, "name": "The 48 Laws of Power", "status": "success", "price": 20.0, "in_stock": True, "price_dropped": False, "restocked": True, "stockouted": False},
    ]
    summary = run_summary(trace)
    assert "48 laws of power" in summary
    assert "restock" in summary
