import re
import json
import requests

def get_hkex_stock_id(ticker: str) -> str:
    """
    Retrieves the stock ID for a given 5-digit HKEX ticker.

    Args:
        ticker: A 5-digit string representing the HKEX ticker (e.g., "02513").

    Returns:
        The stock ID as a string.

    Raises:
        ValueError: If the ticker is invalid, the request fails, response format is incorrect,
                    or no stock ID is found.
    """
    # Validate ticker format
    if not isinstance(ticker, str):
        raise ValueError(f"Ticker must be a string, got {type(ticker)}")
    
    ticker = ticker.strip()
    if len(ticker) != 5 or not ticker.isdigit():
        raise ValueError(f"Ticker must be a 5-digit numeric string, got '{ticker}'")

    url = f"https://www1.hkexnews.hk/search/prefix.do?&callback=callback&lang=ZH&type=A&market=SEHK&name={ticker}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        raise ValueError(f"Failed to fetch stock ID for ticker '{ticker}' due to network/HTTP error: {e}")

    text = response.text.strip()
    
    # Extract JSON from JSONP format: callback(...)
    match = re.match(r"^callback\((.*)\);?$", text, re.DOTALL)
    if not match:
        raise ValueError(f"Unexpected response format from HKEX API: {text[:200]}")
    
    json_str = match.group(1)
    try:
        data = json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON response: {e}. Raw JSON string: {json_str[:200]}")

    stock_info = data.get("stockInfo")
    if not stock_info or not isinstance(stock_info, list):
        raise ValueError(f"No stockInfo found in the API response for ticker '{ticker}'")

    # Retrieve stockId from the first item
    first_item = stock_info[0]
    stock_id = first_item.get("stockId")
    if stock_id is None:
        raise ValueError(f"No stockId found in the first stockInfo item for ticker '{ticker}'")

    # Return stockId as string
    return str(stock_id)
