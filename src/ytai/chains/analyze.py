from __future__ import annotations
import os
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from ytai.config import settings

# ---- LLM (OpenAI by default, optional watsonx) ----

def build_llm():
    if settings.llm_provider == "watsonx":
        try:
            from langchain_ibm import WatsonxLLM
            creds = {"apikey": settings.watsonx_apikey, "url": settings.watsonx_url}
            return WatsonxLLM(
                model_id=settings.watsonx_model_id,
                project_id=settings.watsonx_project_id,
                params={"max_new_tokens": 256, "temperature": 0.3},
                credentials=creds,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize watsonx LLM: {e}")
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=settings.openai_model, temperature=0.3)

llm = build_llm()

# ---- Prompts ----
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful YouTube assistant. Summarize clearly and concisely."),
    ("user", (
        "Video: {title} by {channel}\n\n"
        "Transcript (may be partial):\n{transcript}\n\n"
        "Return a short summary (5-7 bullets) and a one-line takeaway."
    )),
])

hashtags_prompt = ChatPromptTemplate.from_messages([
    ("system", "Generate 5-8 short, relevant hashtags for discoverability."),
    ("user", "Video title: {title}\nSummary: {summary}\nReturn as a comma-separated line, no # symbol."),
])

ideas_prompt = ChatPromptTemplate.from_messages([
    ("system", "Create catchy follow-up video ideas based on the content."),
    ("user", "Give 3 title ideas for a follow-up video related to: {title}."),
])

# ---- LCEL chains ----
summary_chain = summary_prompt | llm | StrOutputParser()
hashtags_chain = hashtags_prompt | llm | StrOutputParser()
ideas_chain = ideas_prompt | llm | StrOutputParser()

# Produce summary, hashtags, and ideas in parallel
analyzer = RunnableParallel({
    "summary": summary_chain,
    "hashtags": ({"title": itemgetter("title"), "summary": itemgetter("summary")} | hashtags_chain),
    "ideas": ({"title": itemgetter("title")} | ideas_chain),
})