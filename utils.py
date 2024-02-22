from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import sys

load_dotenv()


def getPath(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    else:
        return filename


client = AsyncOpenAI()

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    with open("api-key.txt") as f:
        api_key = f.read().strip()

history = []


async def getGPTResponse(message):
    global history
    history.append({"role": "user", "content": message})
    client.api_key = api_key
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=history[-6:]
        + [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
    )
    history.append(
        {"role": "assistant", "content": response.choices[0].message.content}
    )
    return response.choices[0].message.content


def resetHistory():
    global history
    history = []
