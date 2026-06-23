import os
from typing import List, Dict, Optional
from datetime import datetime

# Mock database of HKEX stock codes
TICKER_TO_STOCK_ID = {
    "TENCENT": "00700",
    "700": "00700",
    "00700": "00700",
    "0700": "00700",
    "ALIBABA": "09988",
    "9988": "09988",
    "09988": "09988",
    "MEITUAN": "03690",
    "3690": "03690",
    "03690": "03690",
}

# Mock database of HKEX filings
MOCK_FILINGS = {
    "00700": [
        {
            "filing_id": "TEN_2025_Q1",
            "title": "Tencent Holdings Limited - 2025 First Quarter Results Announcement",
            "date": "2025-05-14",
            "content": """
TENCENT HOLDINGS LIMITED - UNAUDITED Q1 2025 FINANCIAL RESULTS

Revenue by Segment:
- Value-added Services (VAS): RMB 79.5 billion (up 8% YoY). Domestic Games revenue increased by 5% to RMB 36.2 billion, driven by successful updates to flagship titles. International Games revenue grew by 12% to RMB 14.5 billion, led by PUBG Mobile and Brawl Stars.
- Online Advertising: RMB 28.5 billion (up 18% YoY), supported by robust demand for Video Accounts ads and improved ad targeting capabilities utilizing our upgraded Hunyuan AI model.
- FinTech and Business Services: RMB 54.3 billion (up 11% YoY). Business Services revenue grew in double digits, benefiting from cloud services scaling up and the deployment of generative AI APIs to enterprise clients.

AI Initiatives:
- Successfully integrated Tencent Hunyuan AI into our advertising system, resulting in a 25% click-through rate improvement for our advertisers.
- Launched Tencent Hunyuan-Turbo model, reducing inference costs by 45% while increasing speed and reasoning capabilities.
- Cloud computing segment registered a 15% increase in AI-related infrastructure hosting services.

Profitability & Cash Flow:
- Operating profit: RMB 52.8 billion (up 16% YoY). Operating margin improved to 32.5% from 30.2% in the previous year.
- Net profit: RMB 41.5 billion (up 15% YoY).
            """
        },
        {
            "filing_id": "TEN_2025_Q2",
            "title": "Tencent Holdings Limited - 2025 Interim Results Announcement (Q2)",
            "date": "2025-08-13",
            "content": """
TENCENT HOLDINGS LIMITED - UNAUDITED Q2 2025 FINANCIAL RESULTS

Revenue & Segments:
- Total Revenue: RMB 168.9 billion (up 10% YoY).
- Value-added Services (VAS): RMB 82.1 billion (up 9% YoY). Domestic Games revenue increased 6% YoY to RMB 38.0 billion. International Games revenue grew 16% YoY to RMB 15.8 billion, showcasing solid growth in both console and mobile titles.
- Online Advertising: RMB 30.2 billion (up 20% YoY), driven by enhanced recommendation algorithms.
- FinTech and Business Services: RMB 56.6 billion (up 13% YoY). Enterprise SaaS revenue doubled YoY, driven by corporate adoption of AI assistants powered by Tencent Hunyuan.

AI Infrastructure & Developments:
- Released the open-source version of Hunyuan-Large, achieving top benchmarks in coding, math, and bilingual chat.
- Tencent Cloud AI suite added 50+ pre-trained APIs for voice synthesis, image recognition, and natural language understanding.
- Internal AI usage expanded: Over 70% of developer teams inside Tencent are now using AI coding assistants (Tencent Copilot), improving developer productivity by 23%.

Financial Position:
- Operating profit: RMB 58.3 billion (up 18% YoY).
- Gross profit margin reached 53.4%, driven by higher-margin revenue mix and supply chain optimization.
            """
        }
    ],
    "09988": [
        {
            "filing_id": "BABA_2025_Q1",
            "title": "Alibaba Group Holding Limited - March Quarter 2025 Results",
            "date": "2025-05-15",
            "content": """
ALIBABA GROUP HOLDING LIMITED - UNAUDITED FINANCIAL RESULTS FOR THE QUARTER ENDED MARCH 31, 2025

Segment Performance:
- Taobao and Tmall Group (TTG): Revenue of RMB 98.5 billion (up 4% YoY). Double-digit growth in purchase frequency and active buyers. Monetization rates remained stable.
- Cloud Intelligence Group (AIDC): Revenue of RMB 27.6 billion (up 12% YoY). AI-related product revenue grew in triple digits for the fourth consecutive quarter. Shift to public cloud usage continues to improve segment profitability.
- Alibaba International Digital Commerce Group (AIDC): Revenue of RMB 29.8 billion (up 28% YoY), led by AliExpress Choice and Trendyol's cross-border expansion.
- Cainiao Smart Logistics Network: Revenue of RMB 26.5 billion (up 18% YoY), driven by cross-border fulfillment services.

AI and Technology:
- Qwen-2.5 models released, leading open-source models globally. Qwen-2.5-72B outperformed GPT-4 on several reasoning evaluations.
- Alibaba Cloud upgraded its AI model development platform (Model Studio), serving over 120,000 corporate clients, up from 90,000 in the previous quarter.
- Fully integrated AI agents into Taobao shopping assistants, resulting in a 14% improvement in search-to-purchase conversion.

EBITDA and Cash Flow:
- Adjusted EBITDA: RMB 32.1 billion (up 6% YoY).
- Cloud Intelligence Group Adjusted EBITDA grew 150% YoY to RMB 1.4 billion, demonstrating strong operating leverage from proprietary software and hardware integration.
            """
        },
        {
            "filing_id": "BABA_2025_Q2",
            "title": "Alibaba Group Holding Limited - June Quarter 2025 Results",
            "date": "2025-08-14",
            "content": """
ALIBABA GROUP HOLDING LIMITED - UNAUDITED FINANCIAL RESULTS FOR THE QUARTER ENDED JUNE 30, 2025

Segment Highlights:
- Total Revenue: RMB 251.2 billion (up 7% YoY).
- Taobao and Tmall Group: Revenue of RMB 114.8 billion (up 5% YoY). Double-digit growth in GMV, driven by high-value customers and active promotion seasons.
- Cloud Intelligence Group: Revenue of RMB 30.1 billion (up 15% YoY). Over 60% of growth driven by AI-related computing power demands and LLM API calls.
- Alibaba International Digital Commerce Group (AIDC): Revenue of RMB 34.6 billion (up 32% YoY), showing rapid user growth in Europe and the Middle East.

AI Infrastructure Expansion:
- Commenced construction of two new hyperscale datacenters in Zhejiang and Guangdong, dedicated to AI high-performance computing clusters.
- Open-sourced Qwen-Coder models, optimized for software engineering tasks, receiving widespread developer adoption.
- Enterprise customers using Model Studio grew to 180,000, illustrating massive enterprise migration to Alibaba Cloud for generative AI.

Financial Highlights:
- Non-GAAP Net Income: RMB 43.7 billion (up 8% YoY).
- Cash and cash equivalents stood at RMB 210.5 billion, supporting ongoing share repurchases ($5.8B spent during the quarter).
            """
        }
    ]
}


def get_stock_id(ticker: str) -> str:
    """
    Look up the 5-digit HKEX stock code/ID for a given company name, ticker, or symbol.
    
    Args:
        ticker: The search string (e.g. "Tencent", "700", "00700", "9988", "BABA")
        
    Returns:
        The 5-digit stock code.
        
    Raises:
        ValueError: If the ticker is not found in the database.
    """
    clean_ticker = ticker.strip().upper()
    
    # Remove common suffixes
    for suffix in [".HK", " HK", " HOLDINGS", " GROUP"]:
        if clean_ticker.endswith(suffix):
            clean_ticker = clean_ticker[:-len(suffix)].strip()
            
    # Search in database
    if clean_ticker in TICKER_TO_STOCK_ID:
        return TICKER_TO_STOCK_ID[clean_ticker]
        
    # Search for partial match
    for key, val in TICKER_TO_STOCK_ID.items():
        if key in clean_ticker or clean_ticker in key:
            return val
            
    raise ValueError(f"Company ticker/name '{ticker}' not found in HKEX database.")


def get_hkex_filings(stock_id: str, start_date: str, end_date: str) -> List[Dict[str, str]]:
    """
    Fetch HKEX filings for a specific stock ID within a date range (YYYY-MM-DD).
    
    Args:
        stock_id: The 5-digit stock ID (e.g., "00700").
        start_date: Start date string in format YYYY-MM-DD.
        end_date: End date string in format YYYY-MM-DD.
        
    Returns:
        List of dictionaries, each containing filing metadata and content.
    """
    # Standardize stock code to 5 digits
    std_stock_id = stock_id.zfill(5)
    
    if std_stock_id not in MOCK_FILINGS:
        return []
        
    filings = MOCK_FILINGS[std_stock_id]
    results = []
    
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        # Fallback to date comparison if format is slightly off, but assume valid formatting for simplicity
        start_dt = datetime.min
        end_dt = datetime.max
        
    for filing in filings:
        filing_dt = datetime.strptime(filing["date"], "%Y-%m-%d")
        if start_dt <= filing_dt <= end_dt:
            results.append(filing)
            
    return results
