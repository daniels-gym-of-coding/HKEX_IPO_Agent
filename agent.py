import os
from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Import mock tools
from tools import get_stock_id, get_hkex_filings

# Load environment variables
load_dotenv()

# Define the State of the LangGraph agent
class AgentState(TypedDict):
    # Inputs
    user_query: str
    
    # Analysis outputs
    ticker: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    extraction_prompt: Optional[str]
    
    # Intermediate data
    stock_id: Optional[str]
    filings: Optional[List[Dict[str, str]]]
    extracted_data: Optional[List[Dict[str, str]]]
    draft_summary: Optional[str]
    reflection: Optional[str]
    
    # Final outputs
    final_summary: Optional[str]
    error: Optional[str]


# Pydantic schema for structured prompt analysis output
class QueryAnalysis(BaseModel):
    ticker: str = Field(
        description="The ticker symbol or company name extracted from the user query (e.g., 'Tencent', 'Alibaba', '9988')."
    )
    start_date: str = Field(
        default="2025-01-01",
        description="The start date for the filing search in YYYY-MM-DD format. Default to '2025-01-01' if not specified or implied by the query."
    )
    end_date: str = Field(
        default="2025-12-31",
        description="The end date for the filing search in YYYY-MM-DD format. Default to '2025-12-31' if not specified or implied by the query."
    )
    extraction_prompt: str = Field(
        description="A specific, clear prompt to apply to each filing to extract the information required by the user query. It should guide the extractor LLM on what metrics, numbers, or details to extract."
    )


# ---------------------------------------------------------------------
# Graph Nodes
# ---------------------------------------------------------------------

def analyze_prompt_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 1: Analyze user query and extract key parameters.
    """
    user_query = state["user_query"]
    
    # Initialize the LLM (requires OPENAI_API_KEY)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(QueryAnalysis)
    
    system_prompt = (
        "You are an expert financial analyst. Your job is to analyze the user's query about HKEX filings "
        "and extract the target company/ticker, target date range, and construct a precise prompt "
        "to extract the requested details from the quarterly filings."
    )
    
    try:
        analysis: QueryAnalysis = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User Query: {user_query}")
        ])
        
        return {
            "ticker": analysis.ticker,
            "start_date": analysis.start_date,
            "end_date": analysis.end_date,
            "extraction_prompt": analysis.extraction_prompt,
            "error": None
        }
    except Exception as e:
        return {
            "error": f"Failed to analyze user query: {str(e)}"
        }


def get_stock_id_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 2: Resolve the company ticker to a 5-digit HKEX stock code.
    """
    if state.get("error"):
        return {}
        
    ticker = state["ticker"]
    try:
        stock_id = get_stock_id(ticker)
        return {"stock_id": stock_id}
    except ValueError as e:
        return {"error": str(e)}


def fetch_filings_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 3: Retrieve filings using stock ID, start date, and end date.
    """
    if state.get("error"):
        return {}
        
    stock_id = state["stock_id"]
    start_date = state["start_date"]
    end_date = state["end_date"]
    
    filings = get_hkex_filings(stock_id, start_date, end_date)
    
    if not filings:
        return {
            "filings": [],
            "error": f"No HKEX filings found for stock ID {stock_id} between {start_date} and {end_date}."
        }
        
    return {"filings": filings}


def extract_information_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 4: Use extraction prompt to extract specific info from each filing.
    """
    if state.get("error"):
        return {}
        
    filings = state["filings"]
    extraction_prompt = state["extraction_prompt"]
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    extracted_data = []
    
    for filing in filings:
        filing_title = filing["title"]
        filing_date = filing["date"]
        content = filing["content"]
        
        system_prompt = (
            f"You are an AI assistant specialized in analyzing HKEX filings.\n"
            f"You need to extract specific details based on this instruction: {extraction_prompt}\n"
            "Provide ONLY the extracted data and direct facts/metrics. Do not add general summary."
        )
        
        prompt = (
            f"Filing: {filing_title}\n"
            f"Date: {filing_date}\n\n"
            f"Content:\n{content}\n"
        )
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ])
        
        extracted_data.append({
            "filing_id": filing["filing_id"],
            "title": filing_title,
            "date": filing_date,
            "extracted_info": response.content.strip()
        })
        
    return {"extracted_data": extracted_data}


def summarize_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 5: Consolidate and summarize all the extracted info.
    """
    if state.get("error"):
        return {}
        
    extracted_data = state["extracted_data"]
    user_query = state["user_query"]
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    # Format the extracted facts for the summarizer
    formatted_facts = ""
    for data in extracted_data:
        formatted_facts += (
            f"--- Filing: {data['title']} ({data['date']}) ---\n"
            f"{data['extracted_info']}\n\n"
        )
        
    system_prompt = (
        "You are an expert financial summarizer. Synthesize the provided extracted points from filings "
        "into a comprehensive draft report that directly answers the user's inquiry. Use professional "
        "tone, highlight key numbers, trends, and segment details."
    )
    
    prompt = (
        f"User Inquiry: {user_query}\n\n"
        f"Extracted Facts:\n{formatted_facts}\n"
        "Draft Summary:"
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ])
    
    return {"draft_summary": response.content.strip()}


def reflect_and_revise_node(state: AgentState) -> Dict[str, Any]:
    """
    Step 6 & 7: Reflect on draft summary and revise for the final response.
    """
    if state.get("error"):
        return {}
        
    draft_summary = state["draft_summary"]
    user_query = state["user_query"]
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    
    # 1. Reflection Step
    reflection_system = (
        "You are a critical quality assurance editor for financial reports. "
        "Review the draft summary against the user's original query. "
        "Identify if any aspect of the query was missed, if there are any contradictions, "
        "or if formatting/clarity could be improved. Output a list of feedback points."
    )
    
    reflection_prompt = (
        f"User Query: {user_query}\n\n"
        f"Draft Summary:\n{draft_summary}\n\n"
        "Provide critical reflection/feedback on how to improve this summary:"
    )
    
    reflection_response = llm.invoke([
        SystemMessage(content=reflection_system),
        HumanMessage(content=reflection_prompt)
    ])
    reflection = reflection_response.content.strip()
    
    # 2. Revision Step
    revision_system = (
        "You are an elite financial analyst. Revise the draft summary incorporating the reflection feedback. "
        "Ensure the output directly answers the user query, has clear headings, clean markdown bullet points, "
        "and is perfectly accurate to the source material. Highlight key metrics in bold."
    )
    
    revision_prompt = (
        f"User Query: {user_query}\n\n"
        f"Draft Summary:\n{draft_summary}\n\n"
        f"Critique/Feedback:\n{reflection}\n\n"
        "Generate the final, polished response:"
    )
    
    revision_response = llm.invoke([
        SystemMessage(content=revision_system),
        HumanMessage(content=revision_prompt)
    ])
    
    return {
        "reflection": reflection,
        "final_summary": revision_response.content.strip()
    }


# ---------------------------------------------------------------------
# Graph Construction & Compilation
# ---------------------------------------------------------------------

def create_agent():
    # Initialize state graph
    builder = StateGraph(AgentState)
    
    # Add nodes
    builder.add_node("analyze_prompt", analyze_prompt_node)
    builder.add_node("get_stock_id", get_stock_id_node)
    builder.add_node("fetch_filings", fetch_filings_node)
    builder.add_node("extract_information", extract_information_node)
    builder.add_node("summarize", summarize_node)
    builder.add_node("reflect_and_revise", reflect_and_revise_node)
    
    # Define execution flow (routing)
    # Define condition to exit early if there is an error
    def route_after_node(state: AgentState) -> str:
        if state.get("error"):
            return "end"
        return "continue"
        
    builder.set_entry_point("analyze_prompt")
    
    builder.add_conditional_edges(
        "analyze_prompt",
        route_after_node,
        {"continue": "get_stock_id", "end": END}
    )
    
    builder.add_conditional_edges(
        "get_stock_id",
        route_after_node,
        {"continue": "fetch_filings", "end": END}
    )
    
    builder.add_conditional_edges(
        "fetch_filings",
        route_after_node,
        {"continue": "extract_information", "end": END}
    )
    
    builder.add_edge("extract_information", "summarize")
    builder.add_edge("summarize", "reflect_and_revise")
    builder.add_edge("reflect_and_revise", END)
    
    # Compile graph
    return builder.compile()
