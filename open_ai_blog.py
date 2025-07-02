import pandas as pd
from openai import OpenAI
import redis
import json
from decouple import config


SECRET_KEY = config('SECRET_API_KEY')
client = OpenAI(api_key=SECRET_KEY)

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def generate_response(user_id, blog_number, user_message, tone="Neutral", audience="General", format="Article", word_count=800):
    key = f"user:{user_id}:blog:{blog_number}"

    if r.exists(key):
        messages = json.loads(r.get(key))
        messages.append({"role": "user", "content": str(user_message)})
    else:
        messages = [{"role": "system", "content": "You are a helpful blog writer."}]
        prompt = f"""
                Write a {format.lower()} blog post about "{user_message}".
                Tone: {tone}.
                Audience: {audience}.
                Word count: Approximately {word_count} words.
                """
        messages.append({"role": "user", "content": str(prompt) })
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=messages
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        r.set(key, json.dumps(messages))
        return {
            "success": True,
            "blog": response.choices[0].message.content
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

result = generate_response(user_id="332", blog_number='449', user_message='Life style', tone="Informative", format="Travel")
print(result)
