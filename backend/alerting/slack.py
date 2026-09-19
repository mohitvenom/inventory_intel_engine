import os
import requests
import json
from typing import Optional

def send_slack_alert(message: str) -> Optional[dict]:
    """
    Sends a message to the configured Slack webhook URL.
    Returns the response JSON (or dict with status) if successful, None if no webhook configured.
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("Warning: SLACK_WEBHOOK_URL is not set. Skipping Slack alert.")
        return None
        
    payload = {
        "text": message
    }
    
    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        return {"status": "success", "status_code": response.status_code, "text": response.text}
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")
        raise e
