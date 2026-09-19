# Alerting Engine

The alerting engine runs natively as part of the LangGraph orchestrator (`send_alerts` node).

## Trigger Rules
Alerts are evaluated at the end of each product scrape based on comparing the current scrape with the last recorded database history:

- **PRICE_DROP**: Fired when `price_dropped == True`. This requires `curr_price < last_price` and `((last_price - curr_price) / last_price) * 100 >= price_drop_threshold_pct`.
- **RESTOCK**: Fired when `restocked == True`. This requires `curr_stock == True` and `last_stock == False` and `notify_on_restock == True`.
- **STOCKOUT**: Fired when `stockouted == True`. This requires `curr_stock == False` and `last_stock == True` and `notify_on_stockout == True`.

## Deduplication Window
To prevent alert spam on high-frequency polling schedules, the engine checks the `alerts_sent` table using the `get_recent_alerts` MCP tool.
- By default, the **dedupe window is 6 hours**.
- If an alert of the same `alert_type` has been sent for the same `product_id` within the last 6 hours, the engine will suppress the subsequent alerts.

## Slack Integration
When an alert fires, it makes a POST request to the `SLACK_WEBHOOK_URL` defined in `.env`.
- The webhook payload format is: `{"text": "*<TYPE>* Alert for <Product Name>!\nSource: <Source>\nPrice: <Price>\nIn Stock: <Stock>"}`
- Only after a successful webhook (`200 OK`) is the alert recorded in the `alerts_sent` table via the `record_alert_sent` MCP tool.
