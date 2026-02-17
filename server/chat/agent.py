import os
from typing import Dict, Any, List
from qdrant_client import QdrantClient, models
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, AIMessage
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import MessagesState
import psycopg

# Load these from Django settings or environment variables
DB_URI = os.getenv("LANGGRAPH_DB_URI", "postgresql://postgres:pg-root@localhost:5432/langgraph-db?sslmode=disable")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-1.5-flash"  # adjust as needed
TOKEN_THRESHOLD = 1_048_576 * 0.25  # 25% of max tokens

#################  Qdrant Client ##############################
rag_client = QdrantClient(url=QDRANT_URL)

def query_against_rag(query: str, top_k: int = 5):
    prefetch = [
        models.Prefetch(
            query=models.Document(text=query, model="sentence-transformers/all-MiniLM-L6-v2"),
            using="all-MiniLM-L6-v2",
            limit=20,
        ),
        models.Prefetch(
            query=models.Document(text=query, model="Qdrant/bm25"),
            using="bm25",
            limit=20,
        ),
    ]
    results = rag_client.query_points(
        "hybrid-search",
        prefetch=prefetch,
        query=models.Document(text=query, model="colbert-ir/colbertv2.0"),
        using="colbertv2.0",
        with_payload=True,
        limit=top_k,
    )
    return results

QUERY_GENERATION_PROMPT = (
    "Role: Intent Extraction Specialist\n"
    "Purpose: Transform user inputs into optimized search queries for a vector database. "
    "You are a silent middleware component; you do not converse with the user.\n\n"
    "Task Logic:\n"
    "1. Analyze Intent: Determine if the user is seeking external information or facts that require database lookup.\n"
    "2. Information Retrieval: If the input is a question, request for facts, or topic requiring context, create a concise, keyword-rich search query capturing core semantic meaning.\n"
    "3. Non-Search Inputs: If the input is a greeting, command to the system, casual remark, or internal logic requiring no external data, output exactly `<NA>`.\n\n"
    "Output Constraints (Strictly Enforced):\n"
    "- No Preamble: Never include phrases like 'The search query is...' or 'Based on your request...'\n"
    "- No Explanation: Do not justify your reasoning\n"
    "- Raw Output: Return only the generated string or `<NA>`\n"
    "- Refinement: Strip conversational filler (e.g., 'please', 'can you tell me') to focus on semantic entities\n\n"
    "Examples:\n"
    "| User Input Type   | Example Input                                        | Expected Output                      |\n"
    "| ----------------- | ---------------------------------------------------- | ------------------------------------ |\n"
    "| Fact Seeking      | 'What is the company policy on remote work in 2024?' | 'company policy remote work 2024'    |\n"
    "| Implicit Question | 'I'm curious about the specs of the new battery.'    | 'specifications new battery features' |\n"
    "| Greeting          | 'Hello, how are you today?'                          | `<NA>`                               |\n"
    "| Command           | 'Summarize the text I just gave you.'                | `<NA>`                               |\n"
    "| Vague Topic       | 'Tell me about photosynthesis.'                      | 'process of photosynthesis mechanisms' |"
)


class State(MessagesState):
    summary: str
    retrieved_docs: List[Dict[str, Any]]
    refined_query: str


def rag_query_node(state: State):
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]

    messages = [SystemMessage(content=QUERY_GENERATION_PROMPT)] + messages
    response = model.invoke(messages)
    return {"refined_query": response.text}

def filter_keys(d):
    keys_to_remove = {"document_id", "user_id"}
    return {k: v for k, v in d.items() if k not in keys_to_remove}

def search_node(state: State):
    search_query = state.get("refined_query", "")
    if search_query and search_query != "<NA>":
        results = query_against_rag(search_query)
        filtered_list = [filter_keys(point.payload) for point in results.points]
        return {"retrieved_docs": filtered_list}
    else:
        return state  # no docs added

def conversation_node(state: State):
    summary = state.get("summary", "")
    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]

    docs = state.get("retrieved_docs", [])
    if docs:
        system_message = f"Searching the user request against vector db yields the following results: {docs}"
        messages = [SystemMessage(content=system_message)] + messages
    else:
        system_message = "Searching the user request against vector db yielded no results"
        messages = [SystemMessage(content=system_message)] + messages

    response = model.invoke(messages)
    if isinstance(response.content, list):
        response.content = response.text

    return {"messages": [response]}

def summarize_conversation(state: State):
    summary = state.get("summary", "")
    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.text, "messages": delete_messages}

def should_summarize(state: State):
    all_text = state.get("summary", "") + " ".join([m.content for m in state["messages"]])
    total_tokens = count_tokens_approximately(all_text)
    if total_tokens > TOKEN_THRESHOLD:
        return "summarize"
    return "end"


def create_graph(checkpointer=None):
    """Builds and returns the compiled StateGraph."""
    workflow = StateGraph(State)

    workflow.add_node("rag_query_node", rag_query_node)
    workflow.add_node("retrieval_node", search_node)
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("summarize_conversation", summarize_conversation)

    workflow.add_edge(START, "rag_query_node")
    workflow.add_edge("rag_query_node", "retrieval_node")
    workflow.add_edge("retrieval_node", "conversation")

    workflow.add_conditional_edges(
        "conversation",
        should_summarize,
        {
            "summarize": "summarize_conversation",
            "end": END
        }
    )

    workflow.add_edge("summarize_conversation", END)

    global model
    model = ChatGoogleGenerativeAI(model=MODEL_NAME, google_api_key=GOOGLE_API_KEY, temperature=0)

    return workflow.compile(checkpointer=checkpointer)

def get_checkpointer():
    """Returns a PostgresSaver instance with a connection pool."""
    conn = psycopg.connect(DB_URI, autocommit=True)
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()  # ensures tables exist
    return checkpointer