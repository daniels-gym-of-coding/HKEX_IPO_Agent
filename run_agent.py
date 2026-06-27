import os
import sys
import json
from dotenv import load_dotenv


from modules.read_research_topic import read_research_topic
from modules.analyze_user_prompt import analyze_user_prompt
from modules.get_hkex_filings import get_hkex_filings
from modules.download_hkex_filings import download_hkex_filings
from modules.analyze_hkex_filings import analyze_hkex_filings
from modules.zip_analysis_results import zip_analysis_results


# Load environment variables from .env
load_dotenv()


# Read the research topic prompt
file_path = "research_topic.txt"
prompt = read_research_topic(file_path)

print(f"Analyzing prompt from {file_path}...")

parsed = analyze_user_prompt(prompt)

print("\n--- Parsed Parameters ---")
print(json.dumps(parsed, indent=2))

# Retrieve filings and save to CSV
print(f"\nRetrieving filings from {parsed.get('start_date')} to {parsed.get('end_date')}...")
filings = get_hkex_filings(
    start_date=parsed.get("start_date"),
    end_date=parsed.get("end_date")
)

print(f"Retrieved {len(filings)} filings and saved to filings/filings.csv")


# Download the filings files
print("\nDownloading filing files...")
download_hkex_filings(csv_path="filings/filings.csv")

# Analyze filings
print("\nRunning filing analysis...")
analyze_hkex_filings(parsed_params=parsed, csv_path="filings/filings.csv")

# Zip individual filing analysis results
print("\nZipping individual filing analysis results...")
zip_analysis_results(
    filings_dir="filings",
    output_filename="analysis_results.zip"
)





