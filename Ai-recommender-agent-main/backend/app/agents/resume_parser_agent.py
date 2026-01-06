"""
Resume Parser Agent using LangGraph
Extracts structured data from resumes
"""
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from app.utils.resume_parser import resume_parser


class ParserState(TypedDict):
    file_path: str
    raw_text: str
    parsed_data: Dict
    errors: List[str]


def extract_text_node(state: ParserState) -> ParserState:
    """Extract text from resume file"""
    file_path = state.get("file_path", "")
    
    try:
        raw_text = resume_parser.extract_text(file_path)
        return {
            **state,
            "raw_text": raw_text
        }
    except Exception as e:
        return {
            **state,
            "errors": state.get("errors", []) + [f"Error extracting text: {str(e)}"]
        }


def parse_data_node(state: ParserState) -> ParserState:
    """Parse resume data using LLM"""
    raw_text = state.get("raw_text", "")
    
    if not raw_text:
        return {
            **state,
            "errors": state.get("errors", []) + ["No text extracted from resume"]
        }
    
    try:
        parsed_data = resume_parser.parse_with_llm(raw_text)
        return {
            **state,
            "parsed_data": parsed_data
        }
    except Exception as e:
        return {
            **state,
            "errors": state.get("errors", []) + [f"Error parsing resume: {str(e)}"]
        }


def create_resume_parser_agent():
    """Create the Resume Parser Agent workflow"""
    workflow = StateGraph(ParserState)
    
    # Add nodes
    workflow.add_node("extract_text", extract_text_node)
    workflow.add_node("parse_data", parse_data_node)
    
    # Set entry point
    workflow.set_entry_point("extract_text")
    
    # Add edges
    workflow.add_edge("extract_text", "parse_data")
    workflow.add_edge("parse_data", END)
    
    return workflow.compile()


# Global agent instance
resume_parser_agent = create_resume_parser_agent()







