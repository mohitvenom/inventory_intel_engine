import json
from typing import TypedDict, Annotated, List, Dict, Any
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

class ProductTask(TypedDict):
    product: dict

class AgentState(TypedDict):
    run_id: int
    watchlist: List[dict]
    product_results: Annotated[List[dict], operator.add]
    summary: str
    error: str

def parse_mcp_result(res):
    if isinstance(res, str):
        return json.loads(res)
    elif isinstance(res, list) and len(res) > 0:
        parsed_items = []
        for item in res:
            try:
                if hasattr(item, 'text'):
                    parsed = json.loads(item.text)
                elif isinstance(item, str):
                    parsed = json.loads(item)
                elif isinstance(item, dict) and "text" in item:
                    parsed = json.loads(item["text"])
                if isinstance(parsed, list):
                    parsed_items.extend(parsed)
                else:
                    parsed_items.append(parsed)
            except Exception:
                pass
        return parsed_items
    elif isinstance(res, dict) and "result" in res:
        return res["result"]
    return res

def create_inventory_graph(tools_dict: Dict[str, Any]):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    async def fetch_watchlist(state: AgentState):
        list_tool = tools_dict["list_watchlist"]
        res = await list_tool.ainvoke({"active_only": True})
        data = parse_mcp_result(res)
        return {"watchlist": data}

    def map_products(state: AgentState):
        return [Send("check_and_record", {"product": p}) for p in state["watchlist"]]

    async def check_and_record(task: ProductTask):
        p = task["product"]
        source = p.get("source")
        ext_id = p.get("external_id")
        
        result_trace = {
            "id": p["id"],
            "name": p["name"],
            "source": source,
            "status": "success",
            "price": None,
            "in_stock": None,
            "price_dropped": False,
            "restocked": False,
            "stockouted": False,
            "error": None
        }
        
        # 1. Fetch current price/stock
        try:
            if source == "amazon":
                check_res = await tools_dict["check_amazon_price"].ainvoke({"asin": ext_id})
            elif source == "ubuy":
                check_res = await tools_dict["check_ubuy_stock"].ainvoke({"product_url": ext_id, "region": p.get("region")})
            else:
                check_res = {"status": "error", "message": f"Unknown source {source}"}
            
            # parse check_res
            check_res = parse_mcp_result(check_res)
            if isinstance(check_res, list) and len(check_res) > 0:
                check_res = check_res[0]
            elif isinstance(check_res, list):
                check_res = {"status": "error", "message": "Empty response"}
            
            if check_res.get("status") == "error":
                result_trace["status"] = "error"
                result_trace["error"] = check_res.get("message")
            else:
                result_trace["price"] = check_res.get("price")
                result_trace["in_stock"] = check_res.get("in_stock")
        except Exception as e:
            result_trace["status"] = "error"
            result_trace["error"] = str(e)

        # 2. Compare with history and record
        if result_trace["status"] != "error":
            # get history
            try:
                price_history = await tools_dict["get_price_history"].ainvoke({"product_id": p["id"], "limit": 1})
                stock_history = await tools_dict["get_stock_history"].ainvoke({"product_id": p["id"], "limit": 1})
                
                price_history = parse_mcp_result(price_history)
                stock_history = parse_mcp_result(stock_history)
                
                last_price = price_history[0]["price"] if price_history and len(price_history) > 0 and price_history[0].get("price") is not None else None
                last_stock = stock_history[0]["in_stock"] if stock_history and len(stock_history) > 0 else None
                
                curr_price = result_trace["price"]
                curr_stock = result_trace["in_stock"]
                
                # Check price drop
                if curr_price is not None and last_price is not None:
                    drop_pct = ((float(last_price) - float(curr_price)) / float(last_price)) * 100
                    if drop_pct >= float(p.get("price_drop_threshold_pct", 5.0)):
                        result_trace["price_dropped"] = True
                
                # Check stock changes
                if p.get("notify_on_restock") and curr_stock is True and last_stock is False:
                    result_trace["restocked"] = True
                if p.get("notify_on_stockout") and curr_stock is False and last_stock is True:
                    result_trace["stockouted"] = True
                    
                # Record results
                if curr_price is not None:
                    await tools_dict["record_price_check"].ainvoke({
                        "product_id": p["id"], 
                        "price": float(curr_price),
                        "currency": check_res.get("currency", "USD")
                    })
                if curr_stock is not None:
                    await tools_dict["record_stock_check"].ainvoke({
                        "product_id": p["id"],
                        "in_stock": curr_stock
                    })
                    
            except Exception as e:
                result_trace["status"] = "error"
                result_trace["error"] = f"History/Record error: {str(e)}"
                
        return {"product_results": [result_trace]}

    async def summarize_run(state: AgentState):
        results = state.get("product_results", [])
        
        prompt = (
            "You are an AI orchestrator for an inventory and price tracking system.\n"
            "Here is the trace of the current check run:\n"
            f"{json.dumps(results, indent=2)}\n\n"
            "Write a short, human-readable summary (2-4 sentences) of what happened this run. "
            "Highlight any successes, failures, price drops, restocks, or stockouts."
        )
        
        response = await llm.ainvoke([SystemMessage(content="You are a helpful assistant."), HumanMessage(content=prompt)])
        
        print(f"\n--- REAL OPENAI API CALL VERIFICATION ---")
        print(f"Model used: {response.response_metadata.get('model_name', 'Unknown')}")
        print(f"Response ID: {response.response_metadata.get('system_fingerprint', 'Unknown')}")
        token_usage = response.response_metadata.get('token_usage', {})
        print(f"Token usage: Prompt: {token_usage.get('prompt_tokens')} / Completion: {token_usage.get('completion_tokens')} / Total: {token_usage.get('total_tokens')}")
        print(f"Summary text: {response.content}")
        print(f"-----------------------------------------\n")
        
        return {"summary": response.content}

    async def send_alerts(state: AgentState):
        from backend.alerting.slack import send_slack_alert
        results = state.get("product_results", [])
        print(f"DEBUG: Entering send_alerts with {len(results)} results")
        
        for r in results:
            if r.get("status") == "error":
                continue
                
            alert_types = []
            if r.get("price_dropped"):
                alert_types.append("price_drop")
            if r.get("restocked"):
                alert_types.append("restock")
            if r.get("stockouted"):
                alert_types.append("stockout")
                
            for at in alert_types:
                # Check dedupe
                try:
                    recent = await tools_dict["get_recent_alerts"].ainvoke({
                        "product_id": r["id"],
                        "alert_type": at,
                        "since_hours": 6
                    })
                    recent = parse_mcp_result(recent)
                    if recent and len(recent) > 0:
                        print(f"Skipping {at} alert for {r['name']} (dedupe: sent {len(recent)} times in last 6h)")
                        continue
                        
                    # Format message
                    msg = f"*{at}* Alert for {r['name']}!\nSource: {r['source']}\nPrice: {r.get('price')}\nIn Stock: {r.get('in_stock')}"
                    
                    # Send alert
                    res = send_slack_alert(msg)
                    if res and res.get("status") == "success":
                        print(f"Slack webhook response: {res.get('status_code')} {res.get('text')}")
                        # Record alert
                        await tools_dict["record_alert_sent"].ainvoke({
                            "product_id": r["id"],
                            "alert_type": at,
                            "message": msg,
                            "channel": "slack"
                        })
                except Exception as e:
                    print(f"Error processing alert {at} for {r['name']}: {e}")
                    
        return {}

    async def finish_run(state: AgentState):
        run_id = state.get("run_id")
        results = state.get("product_results", [])
        summary = state.get("summary", "")
        
        error_count = sum(1 for r in results if r.get("status") == "error")
        success_count = len(results) - error_count
        
        if success_count == len(results) and len(results) > 0:
            run_status = "success"
        elif error_count == len(results) and len(results) > 0:
            run_status = "failed"
        else:
            run_status = "partial_failure"
        
        trace = {
            "summary": summary,
            "results": results
        }
        
        finish_tool = tools_dict["finish_agent_run"]
        await finish_tool.ainvoke({
            "run_id": run_id,
            "status": run_status,
            "products_checked": len(results),
            "trace": trace,
            "error": state.get("error")
        })
        return {}

    workflow = StateGraph(AgentState)
    
    workflow.add_node("fetch_watchlist", fetch_watchlist)
    workflow.add_node("check_and_record", check_and_record)
    workflow.add_node("send_alerts", send_alerts)
    workflow.add_node("summarize_run", summarize_run)
    workflow.add_node("finish_run", finish_run)
    
    workflow.add_edge(START, "fetch_watchlist")
    workflow.add_conditional_edges("fetch_watchlist", map_products, ["check_and_record"])
    workflow.add_edge("check_and_record", "send_alerts")
    workflow.add_edge("send_alerts", "summarize_run")
    workflow.add_edge("summarize_run", "finish_run")
    workflow.add_edge("finish_run", END)
    
    return workflow.compile()
