from typing import Dict, List, Union

from openai import AsyncOpenAI


async def get_openapi_response(
    messages: List[Dict[str, Union[str, None]]], client: AsyncOpenAI
) -> str:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=1000,
    )

    return response.choices[0].message.content.strip() or "OpenAI вернул пустой ответ."
