from app.services.rag_service import query_rag
from app.db.vector_store import load_chunks
from groq import Groq
from app.core.config import GROQ_API_KEY

# Debug: check API key
print("DEBUG KEY:", GROQ_API_KEY)

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


# =========================
# 🧰 TOOLS
# =========================

# TOOL 1: Search (RAG)
def search_tool(query):
    return query_rag(query)


# TOOL 2: Summarize document
def summarize_tool():
    chunks = load_chunks()

    if not chunks:
        return "No documents available to summarize."

    full_text = " ".join(chunks[:20])  # limit size
    return f"Summary:\n{full_text[:1000]}"


# TOOL 3: Calculator
def calculator_tool(expression):
    try:
        return str(eval(expression))
    except Exception:
        return "Invalid calculation"


# =========================
# 🧠 AGENT DECISION
# =========================

def agent_decision(user_query):
    try:
        prompt = f"""
        You are an AI agent.

        Decide which tool to use:
        - search
        - summarize
        - calculator

        Return ONLY ONE WORD from above.

        Query:
        {user_query}
        """

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )

        if not response.choices:
            return "search"

        output = response.choices[0].message.content.strip().lower()

        print("RAW DECISION:", output)

        if "search" in output:
            return "search"
        elif "summarize" in output:
            return "summarize"
        elif "calculator" in output:
            return "calculator"
        else:
            return "search"  # fallback

    except Exception as e:
        print("Decision Error:", str(e))
        return "search"


# =========================
# 🤖 MAIN AGENT EXECUTION
# =========================

def run_agent(user_query):
    try:
        query_lower = user_query.lower()

        # 🔥 RULE-BASED OVERRIDE (IMPORTANT)
        if "summary" in query_lower or "summarize" in query_lower:
            print("Forced Decision: summarize")
            return summarize_tool()

        if any(op in query_lower for op in ["+", "-", "*", "/"]):
            print("Forced Decision: calculator")
            return calculator_tool(user_query)

        # Otherwise use LLM decision
        decision = agent_decision(user_query)
        print("Final Decision:", decision)

        if decision == "search":
            return search_tool(user_query)

        elif decision == "summarize":
            return summarize_tool()

        elif decision == "calculator":
            return calculator_tool(user_query)

        else:
            return "Sorry, I couldn't decide what to do."

    except Exception as e:
        print("AGENT ERROR:", str(e))
        return f"Error occurred: {str(e)}"