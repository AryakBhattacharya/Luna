from openai import OpenAI
from services.config_loader import load_model_config

client = OpenAI()


def generate_response(
    messages,
    temperature=None,
    max_tokens=None,
    top_p=None,
    return_raw=False
):
    """
    Sends chat completion request to OpenAI.

    Parameters:
    - messages: list of dicts (chat format)
    - temperature: optional override
    - max_tokens: optional override
    - top_p: optional override
    - return_raw: if True, return full response object

    Returns:
    - response text (default)
    - or full API response if return_raw=True
    """

    config = load_model_config()

    response = client.chat.completions.create(
        model=config["model"],
        messages=messages,
        temperature=temperature if temperature is not None else config["temperature"],
        max_tokens=max_tokens if max_tokens is not None else config["max_tokens"],
        top_p=top_p if top_p is not None else config["top_p"],
    )

    if return_raw:
        return response

    return response.choices[0].message.content