import os
from typing import List, Dict, Any, Annotated, Literal
from operator import add
from functools import partial

from qdrant_client import QdrantClient, models
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver
from pydantic import BaseModel


QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
COLLECTION_NAME = "hybrid-search"
MODEL_FAST = "gemini-3-flash"
MODEL_SLOW = "gemini-2.5-pro"        


qdrant_client = QdrantClient(url=QDRANT_URL)
fast_llm = ChatGoogleGenerativeAI(model=MODEL_FAST, google_api_key=GOOGLE_API_KEY, temperature=0)
slow_llm = ChatGoogleGenerativeAI(model=MODEL_SLOW, google_api_key=GOOGLE_API_KEY, temperature=0)


class QuizState(BaseModel):
    messages: Annotated[List[Any], add_messages] = []
    document_ids: List[int] = []
    research_context: Annotated[List[Dict[str, Any]], add] = []   
    search_terms: List[str] = []                 
    summary: str = ""                            
    quiz_structure: str = ""
    critic_comments: str = ""
    iterations: int = 0
    final_quiz: List[Dict[str, Any]] = []
    human_feedback: str = ""


def filter_keys(d: Dict) -> Dict:
    keys_to_remove = {"document_id", "user_id"}
    return {k: v for k, v in d.items() if k not in keys_to_remove}


def retrieve_docs(terms: List[str], doc_ids: List[int]) -> List[Dict[str, Any]]:
    """
    Query Qdrant using hybrid search (dense + sparse) and return deduplicated results.
    """
    if not terms:
        return []
    doc_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="document_id",
                match=models.MatchAny(any=doc_ids)
            )
        ]
    ) if doc_ids else None

    prefetches = []
    for term in terms:
        prefetches.extend([
            models.Prefetch(
                query=models.Document(text=term, model="sentence-transformers/all-MiniLM-L6-v2"),
                using="all-MiniLM-L6-v2",
                filter=doc_filter,
                limit=20,
            ),
            models.Prefetch(
                query=models.Document(text=term, model="Qdrant/bm25"),
                using="bm25",
                filter=doc_filter,
                limit=20,
            ),
        ])

    request = models.QueryRequest(
        prefetch=prefetches,
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        filter=doc_filter,
        with_payload=True,
        limit=10,
    )
    results = qdrant_client.query_batch_points(
        collection_name=COLLECTION_NAME,
        requests=[request]
    )
    points = results[0].points if results else []
    return [filter_keys(p.payload) for p in points]

def generate_initial_terms(state: QuizState) -> Dict[str, Any]:
    """Generate first set of search terms from user request."""
    last_message = state.messages[-1] if state.messages else None
    user_request = last_message.content if last_message and isinstance(last_message, HumanMessage) else ""

    prompt = (
        "Role: Content Explorer Specialist\n"
        "Task: Generate 5-7 specific search terms to find relevant document chunks for quiz creation.\n"
        f"User request: {user_request}\n"
        "Output each term on a new line. No explanations."
    )
    response = fast_llm.invoke([SystemMessage(content=prompt)])
    terms = response.content.strip().split('\n')
    return {"search_terms": terms}

def retrieve_and_add(state: QuizState) -> Dict[str, Any]:
    """Retrieve documents using current search terms and append to research_context."""
    if not state.search_terms:
        return {}
    docs = retrieve_docs(state.search_terms, state.document_ids)
    return {"research_context": docs}

def generate_additional_terms(state: QuizState) -> Dict[str, Any]:
    """Generate more targeted terms based on already retrieved context."""
    prompt = (
        "Role: Topics Predictor Specialist\n"
        "You have already retrieved some document chunks. Based on the user request and these chunks, "
        "generate 5-7 additional search terms to broaden and deepen the search.\n"
        f"User request: {state.messages[-1].content if state.messages else ''}\n"
        f"Existing chunks: {state.research_context[:5]}\n" 
        "Output each term on a new line. No explanations."
    )
    response = fast_llm.invoke([SystemMessage(content=prompt)])
    terms = response.content.strip().split('\n')
    return {"search_terms": terms}

def summarize_context(state: QuizState) -> Dict[str, Any]:
    """Summarise all retrieved documents into a coherent overview for quiz design."""
    if not state.research_context:
        return {"summary": "No relevant documents found."}
    chunks_text = "\n---\n".join([str(c) for c in state.research_context])
    prompt = (
        "Summarize the following research context for creating educational quizzes. "
        "Focus on key concepts, definitions, and facts that can be tested.\n"
        f"User request: {state.messages[-1].content if state.messages else ''}\n"
        f"Research context:\n{chunks_text}\n"
        "Provide a concise, structured summary."
    )
    response = slow_llm.invoke([SystemMessage(content=prompt)])
    return {"summary": response.content}

def generate_structure(state: QuizState) -> Dict[str, Any]:
    """Generate a quiz structure (topics + question types) based on summary and feedback."""
    feedback = ""
    if state.critic_comments:
        feedback = f"Previous critique: {state.critic_comments}\n"
    if state.human_feedback:
        feedback += f"Human feedback: {state.human_feedback}\n"

    prompt = (
        "Role: Quiz Structure Generator\n"
        "Based on the following summary of materials, generate a numbered list of quiz topics "
        "with appropriate question types. Use only these types: MCQ, Open Text Question, Multiple Select Question.\n"
        f"Summary:\n{state.summary}\n"
        f"{feedback}"
        "Output the structure exactly like:\n"
        "1. Topic Name (Question Type)\n"
        "2. Next Topic (Question Type)\n"
        "..."
    )
    response = slow_llm.invoke([SystemMessage(content=prompt)])
    return {
        "quiz_structure": response.content,
        "iterations": state.iterations + 1
    }

def critic_structure(state: QuizState) -> Dict[str, Any]:
    """Review the generated structure and provide feedback."""
    prompt = (
        "Role: Quiz Structure Reviewer\n"
        "Review the following quiz structure based on the provided materials.\n"
        f"Materials summary:\n{state.summary}\n"
        f"Quiz structure draft:\n{state.quiz_structure}\n"
        "Evaluate topic coverage, appropriateness of question types, and any missing topics.\n"
        "Provide constructive feedback. If the structure is good and ready for question generation, "
        "end with the word 'ACCEPTED' on a new line."
    )
    response = slow_llm.invoke([SystemMessage(content=prompt)])
    content = response.content
    status = "accepted" if "ACCEPTED" in content else "rejected"
    return {
        "critic_comments": content,
        "human_feedback": "", 
    }

def generate_questions(state: QuizState) -> Dict[str, Any]:
    """Generate actual quiz questions based on structure and materials."""
    prompt = (
        "Role: Quiz Question Writer\n"
        "Using the approved quiz structure and the materials summary, write actual quiz questions.\n"
        f"Materials summary:\n{state.summary}\n"
        f"Quiz structure:\n{state.quiz_structure}\n"
        "For each item in the structure, generate:\n"
        "- The question text\n"
        "- For MCQ/Multiple Select, provide answer choices\n"
        "- The correct answer(s)\n"
        "Format the output as JSON list of objects with keys: topic, question_type, question, choices (if applicable), answer."
    )
    response = slow_llm.invoke([SystemMessage(content=prompt)])
    import json
    import re
    content = response.content
    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    try:
        questions = json.loads(content)
    except:
        questions = [{"error": "Failed to parse questions", "raw": content}]
    return {"final_quiz": questions}


def should_continue(state: QuizState) -> Literal["generate_structure", "generate_questions"]:
    """Decide whether to refine structure or move to question generation."""
    if state.iterations >= 3:
        return "generate_questions"
    if "ACCEPTED" in state.critic_comments:
        return "generate_questions"
    return "generate_structure"

def create_quiz_graph(checkpointer=None):
    workflow = StateGraph(QuizState)

    # Add nodes
    workflow.add_node("generate_initial_terms", generate_initial_terms)
    workflow.add_node("retrieve_docs", retrieve_and_add)
    workflow.add_node("generate_additional_terms", generate_additional_terms)
    workflow.add_node("retrieve_docs2", retrieve_and_add)   # reuse same function
    workflow.add_node("summarize_context", summarize_context)
    workflow.add_node("generate_structure", generate_structure)
    workflow.add_node("critic_structure", critic_structure)
    workflow.add_node("generate_questions", generate_questions)

    # Edges
    workflow.add_edge(START, "generate_initial_terms")
    workflow.add_edge("generate_initial_terms", "retrieve_docs")
    workflow.add_edge("retrieve_docs", "generate_additional_terms")
    workflow.add_edge("generate_additional_terms", "retrieve_docs2")
    workflow.add_edge("retrieve_docs2", "summarize_context")
    workflow.add_edge("summarize_context", "generate_structure")
    workflow.add_edge("generate_structure", "critic_structure")

    workflow.add_conditional_edges(
        "critic_structure",
        should_continue,
        {
            "generate_structure": "generate_structure",
            "generate_questions": "generate_questions"
        }
    )
    workflow.add_edge("generate_questions", END)

    return workflow.compile(checkpointer=checkpointer)