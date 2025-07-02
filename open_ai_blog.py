from openai import OpenAI
import redis
import json
from decouple import config

SECRET_KEY = config('SECRET_API_KEY')
client = OpenAI(api_key=SECRET_KEY)

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def generate_response(user_id, user_message, tone="Neutral", audience="General", format="Article", word_count=800):
    key = f"user:{user_id}:chat"
    if r.exists(key):
        messages = json.loads(r.get(key))
    else:
        messages = [{"role": "system", "content": "You are a helpful blog writer."}]
    messages.append({"role": "user", "content": str(user_message) })
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

result = generate_response(user_id="566", user_message='Can you suggest me some restaurants with location', tone="Informative", format="Travel Blog")
# print(result["blog"] if result["success"] else result["error"])
print(result)