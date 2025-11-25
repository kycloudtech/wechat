from openai import OpenAI
from dotenv import load_dotenv

import os
import json

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client with environment variables
client = OpenAI(
    api_key=os.getenv("VOLCES_API_KEY"),
    base_url=os.getenv("VOLCES_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
)

default_model = os.getenv("VOLCES_MODEL", "ep-20250210182716-gfw9b")


def call_model(user_content, system_content="", response_format="text", model=default_model):
    completion = client.chat.completions.create(
        model=model,
        response_format={"type": response_format},
        temperature=0,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
    )

    return completion.choices[0].message.dict()["content"]