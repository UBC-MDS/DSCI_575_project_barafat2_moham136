import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Import your existing semantic search from Milestone 1
from semantic_search import semantic_search

load_dotenv()


# 1. LLM SETUP

def load_llm():
    """Instantiate and return the LLaMA-3 chat model via HuggingFace endpoint."""

    llm_endpoint = HuggingFaceEndpoint(
        repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
        task="text-generation",
        max_new_tokens=300,
        provider="auto"
    )
    return ChatHuggingFace(llm=llm_endpoint)


# 2. RETRIEVER: wraps your semantic_search as a LangChain retriever

def retrieve_context(query: str, top_k: int = 5) -> str:
    """
    Calls your Milestone 1 semantic_search and formats the results
    into a plain text context block for the LLM prompt.
    """
    results = semantic_search(query, top_k=5)

    context_parts = []
    for i, row in results.iterrows():
        part = (
            f"Product: {row['product_title']}\n"
            f"Review: {row['text']}\n"
            f"Rating: {row['rating']}\n"
            f"Similarity distance: {row['score']:.4f}"
        )
        context_parts.append(part)

    return "\n\n---\n\n".join(context_parts)


# 3. PROMPT TEMPLATE

PROMPT_TEMPLATE = """
You are a helpful product recommendation assistant.
Use ONLY the product information provided below to answer the user's question.
If the products do not match the query well, say so honestly.

Retrieved Products:
{context}

User Question: {question}

Your Answer:
"""

prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)


# 4. RAG PIPELINE

def build_rag_pipeline():
    """Build and return a LangChain RAG chain: retrieve context, fill prompt, call LLM."""

    llm = load_llm()

    # Chain: retrieve context -> fill prompt -> call LLM
    chain = (
        {
            "context": lambda x: retrieve_context(x["question"]),
            "question": RunnablePassthrough() | (lambda x: x["question"])
        }
        | prompt
        | llm
    )

    return chain


def rag_query(question: str, top_k: int = 5) -> str:
    """
    Main entry point. Pass a natural language product question,
    get a grounded answer back.
    """
    llm = load_llm()

    # Retrieve context from your FAISS index
    context = retrieve_context(question, top_k=top_k)

    # Fill the prompt
    filled_prompt = prompt.invoke({
        "context": context,
        "question": question
    })

    # Call the LLM
    response = llm.invoke(filled_prompt)
    return response.content
