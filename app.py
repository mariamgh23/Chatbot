import streamlit as st
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import os

# --- Chatbot Logic (Extracted from Notebook) ---

class State(TypedDict):
    query: str
    category: str
    sentiment: str
    response: str

# Initialize LLM
llm = ChatOllama(
    model="llama3",
    temperature=0
)

# Nodes
def categorize(state: State) -> State:
    """Categorize the customer query into Technical, Billing, or General."""
    prompt = ChatPromptTemplate.from_template(
        "Categorize the following customer query into one of these categories: "
        "Technical, Billing, General.\n"
        "Respond with ONLY the category name.\n"
        "Query: {query}"
    )
    chain = prompt | llm
    category = chain.invoke({"query": state["query"]}).content.strip()
    return {"category": category}

def analyze_sentiment(state: State) -> State:
    """Analyze the sentiment of the customer query."""
    prompt = ChatPromptTemplate.from_template(
        "Analyze the sentiment of the following customer query.\n"
        "Respond with ONLY one word: Positive, Neutral, or Negative.\n"
        "Query: {query}"
    )
    chain = prompt | llm
    sentiment = chain.invoke({"query": state["query"]}).content.strip()
    return {"sentiment": sentiment}

def handle_technical(state: State) -> State:
    """Provide a technical support response."""
    prompt = ChatPromptTemplate.from_template(
        "You are a technical support agent.\n"
        "Provide a clear and helpful response to the following query:\n"
        "{query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}

def handle_billing(state: State) -> State:
    """Provide a billing support response."""
    prompt = ChatPromptTemplate.from_template(
        "You are a billing support agent.\n"
        "Provide a clear and professional response to the following query:\n"
        "{query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}

def handle_general(state: State) -> State:
    """Provide a general support response."""
    prompt = ChatPromptTemplate.from_template(
        "You are a customer support agent.\n"
        "Provide a helpful response to the following query:\n"
        "{query}"
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]}).content
    return {"response": response}

def escalate(state: State) -> State:
    """Escalate the query to a human agent."""
    return {
        "response": (
            "This query has been escalated to a human agent "
            "due to negative sentiment."
        )
    }

def route_query(state: State) -> str:
    """Route the query based on its sentiment and category."""
    if state["sentiment"] == "Negative":
        return "escalate"
    elif state["category"] == "Technical":
        return "handle_technical"
    elif state["category"] == "Billing":
        return "handle_billing"
    else:
        return "handle_general"

# Create graph and configure
workflow = StateGraph(State)
workflow.add_node("categorize", categorize)
workflow.add_node("analyze_sentiment", analyze_sentiment)
workflow.add_node("handle_technical", handle_technical)
workflow.add_node("handle_billing", handle_billing)
workflow.add_node("handle_general", handle_general)
workflow.add_node("escalate", escalate)

workflow.add_edge("categorize", "analyze_sentiment")
workflow.add_conditional_edges(
    "analyze_sentiment",
    route_query,
    {
        "handle_technical": "handle_technical",
        "handle_billing": "handle_billing",
        "handle_general": "handle_general",
        "escalate": "escalate"
    }
)

workflow.add_edge("handle_technical", END)
workflow.add_edge("handle_billing", END)
workflow.add_edge("handle_general", END)
workflow.add_edge("escalate", END)

workflow.set_entry_point("categorize")
app = workflow.compile()

def run_customer_support(query: str) -> Dict[str, str]:
    """Process a customer query through the LangGraph workflow."""
    results = app.invoke({"query": query})
    return {
        "category": results["category"],
        "sentiment": results["sentiment"],
        "response": results["response"]
    }

# --- Streamlit UI ---

st.set_page_config(page_title="Customer Support 24/7", layout="centered")

# Dark theme styling
st.markdown("""
<style>
.main {
    background-color: #0e1117;
    color: #ffffff;
}

.stTextInput > div > div > input {
    background-color: #262730;
    color: #ffffff;
}

.stButton > button {
    background-color: #4CAF50;
    color: white;
    border-radius: 5px;
}

.chat-bubble {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}

/* Lighter blue (user) */
.user-bubble {
    background-color: #3b82f6;
    text-align: left;
}

/* Lighter gray (bot) */
.bot-bubble {
    background-color: #4b5563;
    text-align: left;
}

/* Softer metadata */
.metadata {
    font-size: 0.8em;
    color: #c7d2fe;
    margin-top: 5px;
}
</style>
""", unsafe_allow_html=True)

st.title("Customer Support 24/7 chatbot")
st.write("Welcome to our automated support system. We're here to help you with technical issues, billing inquiries, and general questions.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble user-bubble"><b>You:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble bot-bubble"><b>Support:</b><br>{message["content"]}<br><div class="metadata">Category: {message["category"]} | Sentiment: {message["sentiment"]}</div></div>', unsafe_allow_html=True)

# Chat input
if query := st.chat_input("How can we help you today?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    st.markdown(f'<div class="chat-bubble user-bubble"><b>You:</b><br>{query}</div>', unsafe_allow_html=True)
    
    with st.spinner("Processing your request..."):
        try:
            result = run_customer_support(query)
            
            # Add bot response to history
            st.session_state.messages.append({
                "role": "bot",
                "content": result["response"],
                "category": result["category"],
                "sentiment": result["sentiment"]
            })
            
            # Display bot response
            st.markdown(f'<div class="chat-bubble bot-bubble"><b>Support:</b><br>{result["response"]}<br><div class="metadata">Category: {result["category"]} | Sentiment: {result["sentiment"]}</div></div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {e}")
