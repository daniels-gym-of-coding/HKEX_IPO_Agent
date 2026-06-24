import os
import csv
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from modules.analyze_single_filing import analyze_single_filing

def analyze_hkex_filings(parsed_params: dict, csv_path: str = "filings/filings.csv") -> None:
    """
    Applies the filing_analyze_prompt from parsed_params to each PDF filing in parallel.
    Uses ThreadPoolExecutor to run tasks concurrently.

    Args:
        parsed_params: Dictionary containing 'filing_analyze_prompt'.
        csv_path: Path to the filings.csv file.

    Raises:
        ValueError: If configuration is missing, CSV is missing, or analysis fails.
    """
    load_dotenv()
    model = os.getenv("LLM_MODEL")
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not model or not api_key:
        raise ValueError("LLM configuration (LLM_MODEL or OPENAI_API_KEY) is missing from the environment.")

    # Normalize CSV path relative to the project root if it is relative
    if not os.path.isabs(csv_path):
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = os.path.join(current_dir, csv_path)

    if not os.path.exists(csv_path):
        raise ValueError(f"CSV file not found at '{csv_path}'. Cannot run analysis.")

    filings_dir = os.path.dirname(csv_path)

    analysis_prompt = parsed_params.get("filing_analyze_prompt")
    if not analysis_prompt:
        raise ValueError("Missing 'filing_analyze_prompt' in the parsed parameters.")

    # Read the filings from CSV
    filings = []
    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filings.append(row)
    except Exception as e:
        raise ValueError(f"Failed to read filings CSV: {e}")

    total = len(filings)
    print(f"Starting parallel analysis for {total} filings with 5 workers...")

    # We use a thread pool with 5 workers as default
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for idx, filing in enumerate(filings, 1):
            futures.append(
                executor.submit(
                    analyze_single_filing,
                    filing=filing,
                    filings_dir=filings_dir,
                    analysis_prompt=analysis_prompt,
                    model=model,
                    api_key=api_key,
                    base_url=base_url,
                    idx=idx,
                    total=total
                )
            )
        # Wait for all futures to complete
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Task generated an exception: {e}")

    print("Completed analysis for all PDF filings.")
