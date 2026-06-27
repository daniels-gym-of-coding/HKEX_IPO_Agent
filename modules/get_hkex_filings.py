import os
import csv
import json
import requests
from datetime import datetime

def get_hkex_filings(start_date: str, end_date: str) -> list:
    """
    Retrieves the list of filings within a date range from the active applications JSON,
    saves the output to a CSV file (filings/filings.csv), and returns the parsed list.

    Args:
        start_date: The start date in YYYYMMDD or YYYY-MM-DD format.
        end_date: The end date in YYYYMMDD or YYYY-MM-DD format.

    Returns:
        A list of dictionaries, where each dictionary contains:
        - "id": The ID of the filing.
        - "name": The company name.
        - "download_link": The absolute URL to download the filing.
        - "filing_date": The filing date formatted as 'YYYY-MM-DD'.
    """
    if not start_date or not end_date:
        raise ValueError("Both start_date and end_date must be provided.")

    def parse_input_date(date_str):
        date_str = str(date_str).strip()
        for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date string: {date_str}")

    start_dt = parse_input_date(start_date)
    end_dt = parse_input_date(end_date)

    url = 'https://www1.hkexnews.hk/ncms/json/eds/appactive_app_sehk_c.json'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        raise ValueError(f"Failed to fetch filings from HKEX: {e}")

    try:
        data = response.json()
    except Exception as e:
        raise ValueError(f"Failed to parse JSON response: {e}")

    app_list = data.get("app", [])
    if not isinstance(app_list, list):
        raise ValueError(f"Expected 'app' to be a list, but got {type(app_list)}")

    target_nf = '申請版本（第一次呈交）'
    link_base = 'https://www.hkexnews.hk/app/'

    def get_appfile(filing_items):
        matches = [item for item in filing_items if item.get('nF') == target_nf and item.get('d')]
        if not matches:
            return None, None
        
        # Sort or find earliest date correctly using datetime objects
        def parse_d(x):
            d_str = x.get('d', '')
            try:
                return datetime.strptime(d_str, "%d/%m/%Y")
            except Exception:
                return datetime.max
        
        earliest_item = min(matches, key=parse_d)
        
        d_val = earliest_item.get('d')
        u1_val = earliest_item.get('u1', '')
        if u1_val:
            link = f"{link_base}{u1_val}"
        else:
            link = None
            
        return d_val, link

    parsed_filings = []
    for item in app_list:
        if not isinstance(item, dict):
            continue

        company = str(item.get("a", "")).strip()
        app_id = str(item.get("id", "")).strip()
        
        ls = item.get("ls", []) or []
        ps = item.get("ps", []) or []
        filing_items = ls + ps

        appdate_str, appfile = get_appfile(filing_items)
        if not appdate_str or not appfile:
            continue

        try:
            appdate_dt = datetime.strptime(appdate_str, "%d/%m/%Y")
        except Exception:
            continue

        # Check if the date is within range
        if start_dt <= appdate_dt <= end_dt:
            parsed_filings.append({
                "id": app_id,
                "name": company,
                "download_link": appfile,
                "filing_date": appdate_dt.strftime("%Y-%m-%d")
            })

    # Sort parsed_filings by filing_date in descending order, then by id
    parsed_filings.sort(key=lambda x: (x["filing_date"], x["id"]), reverse=True)

    # Save to filings/filings.csv
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filings_dir = os.path.join(current_dir, "filings")
    os.makedirs(filings_dir, exist_ok=True)
    csv_path = os.path.join(filings_dir, "filings.csv")

    try:
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "download_link", "filing_date"])
            for f_dict in parsed_filings:
                writer.writerow([
                    f_dict["id"],
                    f_dict["name"],
                    f_dict["download_link"],
                    f_dict["filing_date"]
                ])
    except Exception as e:
        raise ValueError(f"Failed to write CSV file at '{csv_path}': {e}")

    return parsed_filings
