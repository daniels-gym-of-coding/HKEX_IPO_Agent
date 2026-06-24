import os
from markitdown import MarkItDown
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def analyze_single_filing(
    filing: dict,
    filings_dir: str,
    analysis_prompt: str,
    model: str,
    api_key: str,
    base_url: str,
    idx: int,
    total: int
) -> None:
    """
    Analyzes a single HKEX filing: converts PDF to text using MarkItDown,
    submits it to the LLM with the provided prompt, and writes the summary
    to a file.
    """
    filing_id = filing.get("id")
    filing_name = filing.get("name", "Unknown Name")
    filing_date = filing.get("filing_date", "Unknown Date")
    download_link = filing.get("download_link", "")

    if not filing_id:
        return

    # Check format and skip non-PDF filings
    parsed_url = download_link.split("?")[0].lower()
    if not parsed_url.endswith(".pdf"):
        print(f"[{idx}/{total}] Skipping non-PDF filing '{filing_id}' (Format: {os.path.splitext(parsed_url)[1] or 'Unknown'}).")
        return

    # Verify local PDF file exists
    pdf_filename = f"{filing_id}.pdf"
    pdf_path = os.path.join(filings_dir, pdf_filename)
    analysis_filename = f"{filing_id}-analysis.txt"
    analysis_path = os.path.join(filings_dir, analysis_filename)

    # Check if already analyzed
    if os.path.exists(analysis_path) and os.path.getsize(analysis_path) > 0:
        print(f"[{idx}/{total}] Analysis file '{analysis_filename}' already exists. Skipping analysis (bypass).")
        return

    if not os.path.exists(pdf_path):
        print(f"[{idx}/{total}] PDF file for '{filing_id}' does not exist at '{pdf_path}'. Skipping.")
        return

    print(f"[{idx}/{total}] Starting text extraction and analysis for '{pdf_filename}'...")

    # Initialize local converters to ensure thread safety
    try:
        md_converter = MarkItDown()
        conversion_res = md_converter.convert(pdf_path)
        raw_text = conversion_res.text_content
    except Exception as e:
        print(f"[{idx}/{total}] Error extracting text from '{pdf_filename}': {e}. Skipping.")
        return

    if not raw_text or not raw_text.strip():
        print(f"[{idx}/{total}] Warning: No text extracted from '{pdf_filename}'. Skipping.")
        return

    # Truncate content to a safe limit to prevent context length errors (e.g. 150,000 chars)
    max_chars = 150000
    if len(raw_text) > max_chars:
        print(f"[{idx}/{total}] Filing text length ({len(raw_text)} chars) exceeds limit. Truncating to first {max_chars} chars.")
        raw_text = raw_text[:max_chars]

    # Initialize LangChain LLM and parser
    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.0
    )

    # Decouple prompt into several parts as required by rules
    core_instruction = (
        "You are an expert financial analyst. Your task is to analyze the text content of a Hong Kong Exchange filing "
        "and execute the user's specific analysis requirements."
    )

    output_format_instruction = (
        "Provide your analysis summary clearly formatted in Markdown."
    )

    input_information = (
        "Filing Name: {filing_name}\n"
        "Filing Date: {filing_date}\n\n"
        "Filing Text Content:\n{filing_text}\n\n"
        "User Analysis Request:\n{analysis_prompt}"
    )

    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            f"[CORE INSTRUCTION]\n{core_instruction}\n\n"
            f"[OUTPUT FORMAT INSTRUCTION]\n{output_format_instruction}"
        ),
        (
            "user",
            f"[INPUT INFORMATION]\n{input_information}"
        )
    ])

    chain = prompt_template | llm | StrOutputParser()

    # Call LLM chain
    try:
        summary = chain.invoke({
            "filing_name": filing_name,
            "filing_date": filing_date,
            "filing_text": raw_text,
            "analysis_prompt": analysis_prompt
        })
    except Exception as e:
        print(f"[{idx}/{total}] Error calling LLM for '{pdf_filename}': {e}. Skipping.")
        return

    # Write output file
    try:
        with open(analysis_path, "w", encoding="utf-8") as out_file:
            out_file.write(f"Filing Name: {filing_name}\n")
            out_file.write(f"Filing Date: {filing_date}\n")
            out_file.write("-" * 50 + "\n")
            out_file.write(summary)
        print(f"[{idx}/{total}] Finished. Analysis written to {analysis_filename}.")
    except Exception as e:
        print(f"[{idx}/{total}] Error writing analysis to file '{analysis_path}': {e}")
