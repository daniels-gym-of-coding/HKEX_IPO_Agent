import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def reflect_on_summary(
    draft_summary_path: str,
    output_filename: str = "final_summary.md"
) -> None:
    """
    Reads the draft summary report, calls the LLM to perform reflection,
    critical review, and self-correction, and writes the polished final
    summary report to the same parent directory.
    """
    load_dotenv()
    model = os.getenv("LLM_MODEL")
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if not model or not api_key:
        raise ValueError("LLM configuration (LLM_MODEL or OPENAI_API_KEY) is missing from the environment.")

    # Determine absolute path of draft summary
    if not os.path.isabs(draft_summary_path):
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        draft_summary_path = os.path.join(current_dir, draft_summary_path)

    parent_dir = os.path.dirname(draft_summary_path)
    output_path = os.path.join(parent_dir, output_filename)

    if not os.path.exists(draft_summary_path):
        print(f"Draft summary file not found at '{draft_summary_path}'. Reflection aborted.")
        return

    print(f"Reading draft summary from {draft_summary_path}...")
    try:
        with open(draft_summary_path, "r", encoding="utf-8") as f:
            draft_summary_content = f.read().strip()
    except Exception as e:
        print(f"Error reading draft summary file: {e}")
        return

    if not draft_summary_content:
        print("Draft summary is empty. Reflection aborted.")
        return

    print("Submitting draft summary for critical reflection and final polishing...")

    # Set up LLM components
    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0.0
    )

    # Decouple prompt into components as required by project rules
    core_instruction = (
        "You are a critical reviewer and senior financial analyst.\n"
        "Your task is to perform reflection and self-correction on a draft research summary report.\n"
        "Review the draft report for analytical rigor, clarity, completeness, logical consistency, "
        "and verify that it addresses the research parameters. Then, generate a polished, final summary report "
        "that corrects any gaps, improves flow and structure, and presents the findings in a professional, audit-ready manner."
    )

    output_format_instruction = (
        "Provide a polished, final Markdown report. Keep the key structured sections from the draft:\n"
        "1. # Executive Summary Report\n"
        "2. ## Executive Summary\n"
        "3. ## Consolidated Summary Table\n"
        "4. ## Detailed Findings\n"
        "5. ## Conclusion and Recommendations\n\n"
        "Refine the language, correct any logical inconsistencies, ensure risk ratings match the analysis details, "
        "and format tables and quotes cleanly."
    )

    input_information = (
        "Draft Summary Content:\n{draft_summary_content}"
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

    try:
        final_report = chain.invoke({
            "draft_summary_content": draft_summary_content
        })
    except Exception as e:
        print(f"Error during reflection summary generation: {e}")
        return

    # Save to the output file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_report)
        print(f"Polished final summary report successfully written to parent directory: {output_filename}")
    except Exception as e:
        print(f"Error writing final summary report to '{output_path}': {e}")
