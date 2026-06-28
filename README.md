# HKEX_IPO_Agent  

## To Refine

Improve instructions on Agent prompts and Doubao Prompts

## Prerequisites

LLM API Key

## Data Source

https://www.hkexnews.hk/index.htm

## Analyze Request

The agent would receive a user prompt stored in <research_topic.txt> to inquire some aspects about IPO companies across certain periods.<br><br>
After analyzing the user prompt, the agent should specify key parameters for collecing filings and a specific prompt to apply on collected filings.<br><br>
To enhance ground truth and tracability here<br>

## Fetch Filings

The agent would fetch HKEX filings list with start_date, end_date.<br>
The agent would download HKEX filings in the list. <br>

## Analyze Filings

for each file, the specific prompt would be used to extract certain information.<br> 
To enhance robustness here, model fallback, pdf chunking/stateful summary.<br>

## Zip filing analysis

The agent would zip up all filing analysis results.

