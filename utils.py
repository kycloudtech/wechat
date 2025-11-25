from openai import OpenAI

import os
import json



client = OpenAI(
    api_key = "a7298f00-f004-47a0-b7bb-023c83c6e38c",
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)

default_model="ep-20250210182716-gfw9b"


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