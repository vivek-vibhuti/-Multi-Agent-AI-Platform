from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.agents import create_agent
from langchain_core.messages.ai import AIMessage
from langchain_core.messages import HumanMessage

from app.config.settings import settings

def get_response_from_ai_agent(llm_id, query, allow_search, system_prompt):
    llm = ChatGroq(model=llm_id, api_key=settings.GROQ_API_KEY)
    tools = [TavilySearchResults(max_results=2)] if allow_search else []
    agent = create_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )
    state = {"messages": query} if isinstance(query, list) else {"messages": [HumanMessage(content=query)]}
    response = agent.invoke(state)
    messages = response.get("messages", [])
    ai_messages = [msg.content for msg in messages if isinstance(msg, AIMessage)]
    return ai_messages[-1] if ai_messages else ""
