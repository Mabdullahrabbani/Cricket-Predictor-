import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def Generate_Description(Prediction_type: str, Prediction: float, ScoreBoard: dict):
    try:
        client = OpenAI(
            api_key=os.getenv("OPEN_Ai_KEY"),
            base_url="https://api.groq.com/openai/v1",
            timeout=20,
        )
        prompt = f"""You are a cricket analyst. A prediction model produced this result:
Prediction type: {Prediction_type}
Predicted value: {Prediction}
Match situation: {ScoreBoard}
In 2-3 simple sentences, explain why this prediction makes sense given the match situation. Write for a casual cricket fan, not a data scientist."""

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Analysis unavailable ({type(e).__name__}: {e})"