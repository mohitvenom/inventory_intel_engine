import pytest
import asyncio
from backend.agent.graph import create_inventory_graph

class MockTool:
    def __init__(self, name, return_val=None, side_effect=None):
        self.name = name
        self.return_val = return_val
        self.side_effect = side_effect
        self.calls = []

    async def ainvoke(self, args):
        self.calls.append(args)
        if self.side_effect:
            return self.side_effect(args)
        return self.return_val

import json

@pytest.fixture
def mock_tools_dict():
    return {
        "list_watchlist": MockTool("list_watchlist", return_val="[]"),
        "check_amazon_price": MockTool("check_amazon_price", return_val=json.dumps({"status": "success", "price": 100.0, "in_stock": True, "currency": "USD"})),
        "check_ubuy_stock": MockTool("check_ubuy_stock", return_val=json.dumps({"status": "success", "price": 100.0, "in_stock": True, "currency": "USD"})),
        "get_price_history": MockTool("get_price_history", return_val=json.dumps([{"price": 100.0, "currency": "USD"}])),
        "get_stock_history": MockTool("get_stock_history", return_val=json.dumps([{"in_stock": True}])),
        "record_price_check": MockTool("record_price_check", return_val="{}"),
        "record_stock_check": MockTool("record_stock_check", return_val="{}"),
        "get_recent_alerts": MockTool("get_recent_alerts", return_val="[]"),
        "record_alert_sent": MockTool("record_alert_sent", return_val="{}"),
        "finish_agent_run": MockTool("finish_agent_run", return_val="{}"),
    }

@pytest.mark.asyncio
async def test_threshold_logic_normal_drop(mock_tools_dict):
    # Current price is 90, last price is 100. 10% drop, threshold is 5%
    mock_tools_dict["check_amazon_price"].return_val = json.dumps({"status": "success", "price": 90.0, "in_stock": True, "currency": "USD"})
    mock_tools_dict["get_price_history"].return_val = json.dumps([{"price": 100.0, "currency": "USD"}])
    
    product = {
        "id": 1,
        "name": "Test Product",
        "source": "amazon",
        "external_id": "B01",
        "price_drop_threshold_pct": 5.0,
        "notify_on_restock": True,
        "notify_on_stockout": True
    }
    mock_tools_dict["list_watchlist"].return_val = json.dumps([product])
    
    from unittest.mock import patch, MagicMock
    with patch("backend.agent.graph.ChatOpenAI") as MockLLM:
        mock_llm_instance = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.content = "Mock summary"
            mock_response.response_metadata = {"model_name": "mock", "system_fingerprint": "mock", "token_usage": {}}
            return mock_response
        mock_llm_instance.ainvoke = mock_ainvoke
        MockLLM.return_value = mock_llm_instance
        
        graph = create_inventory_graph(mock_tools_dict)
        res = await graph.ainvoke({"run_id": 1, "product_results": []})
        
    results = res["product_results"]
    assert len(results) == 1
    assert results[0]["price_dropped"] is True
    assert results[0]["restocked"] is False
    assert results[0]["stockouted"] is False

@pytest.mark.asyncio
async def test_threshold_logic_exact_boundary(mock_tools_dict):
    # Current price 95, last price 100. Exactly 5.0% drop. Threshold 5.0%.
    mock_tools_dict["check_amazon_price"].return_val = json.dumps({"status": "success", "price": 95.0, "in_stock": True, "currency": "USD"})
    mock_tools_dict["get_price_history"].return_val = json.dumps([{"price": 100.0, "currency": "USD"}])
    
    product = {
        "id": 1, "name": "Test Product", "source": "amazon", "external_id": "B01",
        "price_drop_threshold_pct": 5.0, "notify_on_restock": True, "notify_on_stockout": True
    }
    mock_tools_dict["list_watchlist"].return_val = json.dumps([product])
    
    from unittest.mock import patch, MagicMock
    with patch("backend.agent.graph.ChatOpenAI") as MockLLM:
        mock_llm_instance = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.content = "Mock summary"
            mock_response.response_metadata = {"model_name": "mock", "system_fingerprint": "mock", "token_usage": {}}
            return mock_response
        mock_llm_instance.ainvoke = mock_ainvoke
        MockLLM.return_value = mock_llm_instance
        
        graph = create_inventory_graph(mock_tools_dict)
        res = await graph.ainvoke({"run_id": 1, "product_results": []})
        
    assert res["product_results"][0]["price_dropped"] is True

@pytest.mark.asyncio
async def test_threshold_logic_no_history(mock_tools_dict):
    # No price history
    mock_tools_dict["check_amazon_price"].return_val = json.dumps({"status": "success", "price": 90.0, "in_stock": True, "currency": "USD"})
    mock_tools_dict["get_price_history"].return_val = "[]" # No history
    mock_tools_dict["get_stock_history"].return_val = "[]" # No history
    
    product = {
        "id": 1, "name": "Test Product", "source": "amazon", "external_id": "B01",
        "price_drop_threshold_pct": 5.0, "notify_on_restock": True, "notify_on_stockout": True
    }
    mock_tools_dict["list_watchlist"].return_val = json.dumps([product])
    
    from unittest.mock import patch, MagicMock
    with patch("backend.agent.graph.ChatOpenAI") as MockLLM:
        mock_llm_instance = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.content = "Mock summary"
            mock_response.response_metadata = {"model_name": "mock", "system_fingerprint": "mock", "token_usage": {}}
            return mock_response
        mock_llm_instance.ainvoke = mock_ainvoke
        MockLLM.return_value = mock_llm_instance
        
        graph = create_inventory_graph(mock_tools_dict)
        res = await graph.ainvoke({"run_id": 1, "product_results": []})
        
    assert res["product_results"][0]["price_dropped"] is False
    assert res["product_results"][0]["restocked"] is False
    assert res["product_results"][0]["stockouted"] is False

@pytest.mark.asyncio
async def test_threshold_logic_restock(mock_tools_dict):
    # Current in_stock True, last in_stock False
    mock_tools_dict["check_amazon_price"].return_val = json.dumps({"status": "success", "price": 100.0, "in_stock": True, "currency": "USD"})
    mock_tools_dict["get_price_history"].return_val = json.dumps([{"price": 100.0, "currency": "USD"}])
    mock_tools_dict["get_stock_history"].return_val = json.dumps([{"in_stock": False}])
    
    product = {
        "id": 1, "name": "Test Product", "source": "amazon", "external_id": "B01",
        "price_drop_threshold_pct": 5.0, "notify_on_restock": True, "notify_on_stockout": True
    }
    mock_tools_dict["list_watchlist"].return_val = json.dumps([product])
    
    from unittest.mock import patch, MagicMock
    with patch("backend.agent.graph.ChatOpenAI") as MockLLM:
        mock_llm_instance = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.content = "Mock summary"
            mock_response.response_metadata = {"model_name": "mock", "system_fingerprint": "mock", "token_usage": {}}
            return mock_response
        mock_llm_instance.ainvoke = mock_ainvoke
        MockLLM.return_value = mock_llm_instance
        
        graph = create_inventory_graph(mock_tools_dict)
        res = await graph.ainvoke({"run_id": 1, "product_results": []})
        
    assert res["product_results"][0]["restocked"] is True
    assert res["product_results"][0]["stockouted"] is False

@pytest.mark.asyncio
async def test_threshold_logic_stockout(mock_tools_dict):
    # Current in_stock False, last in_stock True
    mock_tools_dict["check_amazon_price"].return_val = json.dumps({"status": "success", "price": 100.0, "in_stock": False, "currency": "USD"})
    mock_tools_dict["get_price_history"].return_val = json.dumps([{"price": 100.0, "currency": "USD"}])
    mock_tools_dict["get_stock_history"].return_val = json.dumps([{"in_stock": True}])
    
    product = {
        "id": 1, "name": "Test Product", "source": "amazon", "external_id": "B01",
        "price_drop_threshold_pct": 5.0, "notify_on_restock": True, "notify_on_stockout": True
    }
    mock_tools_dict["list_watchlist"].return_val = json.dumps([product])
    
    from unittest.mock import patch, MagicMock
    with patch("backend.agent.graph.ChatOpenAI") as MockLLM:
        mock_llm_instance = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.content = "Mock summary"
            mock_response.response_metadata = {"model_name": "mock", "system_fingerprint": "mock", "token_usage": {}}
            return mock_response
        mock_llm_instance.ainvoke = mock_ainvoke
        MockLLM.return_value = mock_llm_instance
        
        graph = create_inventory_graph(mock_tools_dict)
        res = await graph.ainvoke({"run_id": 1, "product_results": []})
        
    assert res["product_results"][0]["restocked"] is False
    assert res["product_results"][0]["stockouted"] is True

@pytest.mark.asyncio
async def test_threshold_logic_null_price(mock_tools_dict):
    # Null price (e.g. ubuy JS rendered)
    mock_tools_dict["check_amazon_price"].return_val = json.dumps({"status": "success", "price": None, "in_stock": True, "currency": "USD"})
    mock_tools_dict["get_price_history"].return_val = json.dumps([{"price": 100.0, "currency": "USD"}])
    mock_tools_dict["get_stock_history"].return_val = json.dumps([{"in_stock": True}])
    
    product = {
        "id": 1, "name": "Test Product", "source": "amazon", "external_id": "B01",
        "price_drop_threshold_pct": 5.0, "notify_on_restock": True, "notify_on_stockout": True
    }
    mock_tools_dict["list_watchlist"].return_val = json.dumps([product])
    
    from unittest.mock import patch, MagicMock
    with patch("backend.agent.graph.ChatOpenAI") as MockLLM:
        mock_llm_instance = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.content = "Mock summary"
            mock_response.response_metadata = {"model_name": "mock", "system_fingerprint": "mock", "token_usage": {}}
            return mock_response
        mock_llm_instance.ainvoke = mock_ainvoke
        MockLLM.return_value = mock_llm_instance
        
        graph = create_inventory_graph(mock_tools_dict)
        res = await graph.ainvoke({"run_id": 1, "product_results": []})
        
    assert res["product_results"][0]["price_dropped"] is False

@pytest.mark.asyncio
async def test_currency_fallback_logic_missing(mock_tools_dict):
    # Mock check_amazon_price to return result without currency
    mock_tools_dict["check_amazon_price"].return_val = json.dumps({"status": "success", "price": 100.0, "in_stock": True})
    mock_tools_dict["get_price_history"].return_val = "[]"
    mock_tools_dict["get_stock_history"].return_val = "[]"
    
    product = {
        "id": 12, "name": "Test Product TR", "source": "amazon", "external_id": "B01",
        "currency": "TRY",
        "price_drop_threshold_pct": 5.0, "notify_on_restock": True, "notify_on_stockout": True
    }
    mock_tools_dict["list_watchlist"].return_val = json.dumps([product])
    
    from unittest.mock import patch, MagicMock
    with patch("backend.agent.graph.ChatOpenAI") as MockLLM:
        mock_llm_instance = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.content = "Mock summary"
            mock_response.response_metadata = {"model_name": "mock", "system_fingerprint": "mock", "token_usage": {}}
            return mock_response
        mock_llm_instance.ainvoke = mock_ainvoke
        MockLLM.return_value = mock_llm_instance
        
        graph = create_inventory_graph(mock_tools_dict)
        res = await graph.ainvoke({"run_id": 1, "product_results": []})
        
    # Assert record_price_check was called with currency "TRY"
    calls = mock_tools_dict["record_price_check"].calls
    assert len(calls) == 1
    assert calls[0]["currency"] == "TRY"

@pytest.mark.asyncio
async def test_currency_fallback_logic_none(mock_tools_dict):
    # Mock check_amazon_price to return result with currency as None
    mock_tools_dict["check_amazon_price"].return_val = json.dumps({"status": "success", "price": 100.0, "in_stock": True, "currency": None})
    mock_tools_dict["get_price_history"].return_val = "[]"
    mock_tools_dict["get_stock_history"].return_val = "[]"
    
    product = {
        "id": 12, "name": "Test Product TR", "source": "amazon", "external_id": "B01",
        "currency": "TRY",
        "price_drop_threshold_pct": 5.0, "notify_on_restock": True, "notify_on_stockout": True
    }
    mock_tools_dict["list_watchlist"].return_val = json.dumps([product])
    
    from unittest.mock import patch, MagicMock
    with patch("backend.agent.graph.ChatOpenAI") as MockLLM:
        mock_llm_instance = MagicMock()
        async def mock_ainvoke(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.content = "Mock summary"
            mock_response.response_metadata = {"model_name": "mock", "system_fingerprint": "mock", "token_usage": {}}
            return mock_response
        mock_llm_instance.ainvoke = mock_ainvoke
        MockLLM.return_value = mock_llm_instance
        
        graph = create_inventory_graph(mock_tools_dict)
        res = await graph.ainvoke({"run_id": 1, "product_results": []})
        
    # Assert record_price_check was called with currency "TRY"
    calls = mock_tools_dict["record_price_check"].calls
    assert len(calls) == 1
    assert calls[0]["currency"] == "TRY"
