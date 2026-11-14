
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def shopping_agent(user_query):

    if not client.api_key:
        return {
            "error": "Groq API key not found. Check your .env file."
        }

    prompt = f"""
    You are TRUSTBUY-AI, an intelligent shopping assistant.

    Analyze the customer's shopping request:
    {user_query}

    Return ONLY valid JSON with these fields:
    {{
        "category": "product category",
        "budget": "budget or null",
        "recommendation": "Helpful shopping advice"
    }}

    Do not invent actual product prices or availability.
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        ai_result = response.choices[0].message.content

        result = json.loads(ai_result)

        return {
            "agent": "TRUSTBUY-AI",
            "user_query": user_query,
            "category": result.get("category"),
            "budget": result.get("budget"),
            "recommendation": result.get("recommendation"),
            "status": "AI analysis successful"
        }

    except Exception as e:
        return {
            "error": str(e)
        }


if __name__ == "__main__":

    query = input("What are you looking for? ")

    print(json.dumps(
        shopping_agent(query),
        indent=4
    ))
