import os
import sys
from dotenv import load_dotenv
from agent import create_agent

# Load environment variables from .env
load_dotenv()

def print_banner(title: str):
    print("=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)

def run_agent_live(query: str):
    print_banner("RUNNING LANGGRAPH AGENT (LIVE)")
    print(f"User Query: {query}\n")
    
    agent = create_agent()
    
    # Initialize state
    initial_state = {"user_query": query}
    
    # Stream the graph execution step by step
    for event in agent.stream(initial_state):
        for node_name, state_update in event.items():
            print(f"\n>>> Node executed: {node_name}")
            
            # Print relevant state updates
            for key, val in state_update.items():
                if key == "error" and val:
                    print(f"  [ERROR] {val}")
                elif key in ["ticker", "start_date", "end_date", "stock_id"]:
                    print(f"  {key}: {val}")
                elif key == "extraction_prompt":
                    print(f"  {key}: \"{val}\"")
                elif key == "filings" and val:
                    print(f"  Found {len(val)} filing(s):")
                    for f in val:
                        print(f"    - {f['title']} (Filing ID: {f['filing_id']}, Date: {f['date']})")
                elif key == "extracted_data" and val:
                    print(f"  Extracted info for {len(val)} filing(s).")
                elif key == "draft_summary":
                    print("\n--- Draft Summary ---")
                    print(val)
                elif key == "reflection":
                    print("\n--- Critique & Reflection ---")
                    print(val)
                elif key == "final_summary":
                    print("\n--- Final Polished Summary ---")
                    print(val)
                    
            print("-" * 60)

def run_agent_simulation(query: str):
    print_banner("LANGGRAPH AGENT SIMULATION MODE")
    print(f"User Query: {query}\n")
    print("NOTE: OPENAI_API_KEY is not set. Simulating graph execution for demonstration.\n")
    
    # Let's simulate step-by-step execution to show what happens under the hood
    print("1. [Node: analyze_prompt]")
    print(f"   Analyzing user query: '{query}'")
    ticker = "Tencent" if "tencent" in query.lower() else "Alibaba"
    print(f"   -> Extracted Ticker: {ticker}")
    print("   -> Target Dates: 2025-01-01 to 2025-12-31")
    print("   -> Generated Extraction Prompt: 'Extract all segment performance, gaming growth, cloud business and AI development metrics.'")
    print("-" * 60)
    
    print("2. [Node: get_stock_id]")
    stock_id = "00700" if ticker == "Tencent" else "09988"
    print(f"   Resolving '{ticker}' using tools.get_stock_id...")
    print(f"   -> Stock ID: {stock_id}")
    print("-" * 60)
    
    print("3. [Node: fetch_filings]")
    print(f"   Fetching filings for stock code {stock_id} between 2025-01-01 and 2025-12-31...")
    if stock_id == "00700":
        filings = [
            "Tencent Holdings Limited - 2025 First Quarter Results Announcement (2025-05-14)",
            "Tencent Holdings Limited - 2025 Interim Results Announcement (Q2) (2025-08-13)"
        ]
    else:
        filings = [
            "Alibaba Group Holding Limited - March Quarter 2025 Results (2025-05-15)",
            "Alibaba Group Holding Limited - June Quarter 2025 Results (2025-08-14)"
        ]
    for f in filings:
        print(f"   -> Found Filing: {f}")
    print("-" * 60)
    
    print("4. [Node: extract_information]")
    print("   Running extraction prompt against all filing contents...")
    if stock_id == "00700":
        extracted = (
            "- Q1 2025: VAS revenue RMB 79.5B (Domestic games up 5% to RMB 36.2B, International games up 12% to RMB 14.5B). Hunyuan AI integration boosted ad CTR by 25%.\n"
            "- Q2 2025: Total Revenue RMB 168.9B. Domestic games RMB 38.0B (up 6%), International games RMB 15.8B (up 16%). 70% of developers use Tencent Copilot."
        )
    else:
        extracted = (
            "- March Q1 2025: Taobao/Tmall revenue RMB 98.5B (up 4%). Cloud Intelligence Group revenue RMB 27.6B (up 12%). Released Qwen-2.5 models.\n"
            "- June Q2 2025: Total Revenue RMB 251.2B (up 7%). Cloud Intelligence Group revenue RMB 30.1B (up 15%), driven by AI computing demands."
        )
    print("   -> Extracted data from filings successfully.")
    print("-" * 60)
    
    print("5. [Node: summarize]")
    print("   Synthesizing extracted points into draft summary...")
    draft = f"Based on Q1 and Q2 2025 reports, {ticker} demonstrated solid growth. " + (
        "Gaming revenue was driven by international titles like PUBG Mobile, and AI (Hunyuan) is driving advertising efficiency and SaaS adoption."
        if stock_id == "00700" else
        "Cloud Intelligence Group grew 12-15% driven by AI computing demands and Model Studio usage, while Taobao/Tmall GMV showed steady growth."
    )
    print(f"\n--- Draft Summary ---\n{draft}")
    print("-" * 60)
    
    print("6. [Node: reflect_and_revise]")
    print("   Reviewing draft summary against user query and editing...")
    reflection = "Critique: The summary captures core segments but could detail exact growth percentages and bold key metrics."
    print(f"\n--- Critique & Reflection ---\n{reflection}")
    
    final = f"### {ticker} 2025 Mid-Year Performance Summary\n\n" + (
        "**Gaming Segment Growth**:\n"
        "- **Domestic Games**: Grew **5% YoY** to RMB 36.2B in Q1, and **6% YoY** to RMB 38.0B in Q2.\n"
        "- **International Games**: Rose **12% YoY** to RMB 14.5B in Q1, and surged **16% YoY** to RMB 15.8B in Q2, showing strong global traction.\n\n"
        "**AI & Cloud Performance**:\n"
        "- **Tencent Hunyuan AI**: Integrated into online ads, boosting CTR by **25%**. Hunyuan-Turbo reduced inference costs by **45%**.\n"
        "- **Developer Adoption**: Over **70%** of internal developer teams utilize AI coding assistants, raising efficiency by **23%**."
        if stock_id == "00700" else
        "**Cloud & AI Business**:\n"
        "- **Revenue**: Cloud Intelligence Group rose **12% YoY** in Q1 (RMB 27.6B) and **15% YoY** in Q2 (RMB 30.1B). AI product revenue grew in triple digits.\n"
        "- **Client Base**: Model Studio corporate clients increased from **90,000** to **180,000** over the two quarters.\n\n"
        "**Core E-Commerce**:\n"
        "- **Taobao & Tmall**: Revenue rose **4%** in Q1 (RMB 98.5B) and **5%** in Q2 (RMB 114.8B) with double-digit buyer frequency growth."
    )
    print(f"\n--- Final Polished Summary ---\n{final}")
    print("-" * 60)

def main():
    # Example queries you can try
    queries = {
        "1": "Can you summarize Tencent's gaming performance and AI initiatives in their Q1 and Q2 2025 reports?",
        "2": "What was Alibaba's cloud and AI revenue growth and key metrics for Q1 and Q2 of 2025?",
    }
    
    print_banner("HKEX FILINGS LANGGRAPH AGENT")
    print("Select a query to run:")
    for num, q in queries.items():
        print(f"  [{num}] {q}")
    print("  [Or type a custom query]")
    
    choice = input("\nEnter choice (1/2 or custom text): ").strip()
    
    if choice in queries:
        query = queries[choice]
    elif choice:
        query = choice
    else:
        query = queries["1"]
        
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key and not api_key.startswith("your_"):
        try:
            run_agent_live(query)
        except Exception as e:
            print(f"\nAn error occurred while running live agent: {e}")
            print("Switching to simulation mode...")
            run_agent_simulation(query)
    else:
        print("\n[SETUP REQUIRED]")
        print("To run the live agent using OpenAI:")
        print("  1. Create a copy of '.env.template' named '.env': cp .env.template .env")
        print("  2. Edit '.env' and fill in your OPENAI_API_KEY")
        print("  3. Run: python main.py again\n")
        
        run_agent_simulation(query)

if __name__ == "__main__":
    main()
