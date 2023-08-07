from typing import Annotated, Union, List

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from pydantic import BaseModel

app = FastAPI()

security = HTTPBasic()


class PostData(BaseModel):
    model_name: str = "llama-2-7b-chat.ggmlv3.q2_K"
    temperature: float = 0.1
    messages: list[Union[SystemMessage, HumanMessage, AIMessage]]
    max_tokens: int = 2000


def get_llm(data: PostData, callback_manager: CallbackManager) -> LlamaCpp:
    # params: https://api.python.langchain.com/en/latest/llms/langchain.llms.llamacpp.LlamaCpp.html
    params = {"temperature": data.temperature,
              "max_tokens": data.max_tokens,
              "top_p": 1
              }
    return LlamaCpp(
        model_path=f"./models/{data.model_name}.bin",
        **params,
        callback_manager=callback_manager,
        verbose=False,  # True
    )


def get_answer(llm, messages) -> str:
    if isinstance(llm, LlamaCpp):
        return llm(llama_v2_prompt(convert_langchainschema_to_dict(messages)))


def find_role(message: Union[SystemMessage, HumanMessage, AIMessage]) -> str:
    """
    Identify role name from langchain.schema object.
    """
    if isinstance(message, SystemMessage):
        return "system"
    if isinstance(message, HumanMessage):
        return "user"
    if isinstance(message, AIMessage):
        return "assistant"
    raise TypeError("Unknown message type.")


def convert_langchainschema_to_dict(
        messages: List[Union[SystemMessage, HumanMessage, AIMessage]]) \
        -> List[dict]:
    """
    Convert the chain of chat messages in list of langchain.schema format to
    list of dictionary format.
    """
    return [{"role": find_role(message),
             "content": message.content
             } for message in messages]


def llama_v2_prompt(messages: List[dict]) -> str:
    """
    Convert the messages in list of dictionary format to Llama2 compliant format.
    """
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    BOS, EOS = "<s>", "</s>"
    DEFAULT_SYSTEM_PROMPT = f"""You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Please ensure that your responses are socially unbiased and positive in nature. If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information."""

    if messages[0]["role"] != "system":
        messages = [
            {
                "role": "system",
                "content": DEFAULT_SYSTEM_PROMPT,
            }
        ] + messages
    messages = [
        {
            "role": messages[1]["role"],
            "content": B_SYS + messages[0]["content"] + E_SYS + messages[1]["content"],
        }
    ] + messages[2:]

    messages_list = [
        f"{BOS}{B_INST} {(prompt['content']).strip()} {E_INST} {(answer['content']).strip()} {EOS}"
        for prompt, answer in zip(messages[::2], messages[1::2])
    ]
    messages_list.append(
        f"{BOS}{B_INST} {(messages[-1]['content']).strip()} {E_INST}")

    return "".join(messages_list)


@app.post("/chat/")
async def post_chat_prompt(data: PostData, credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> str:
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm = get_llm(data, callback_manager)
    print(f"Model: {data.model_name}, getting response...")
    results = await get_answer(llm, data.messages)
    return results
