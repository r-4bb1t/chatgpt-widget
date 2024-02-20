from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncOpenAI()
api_key = os.getenv("OPENAI_API_KEY")


async def get_gpt_response(message):
    client.api_key = api_key
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content
