from typing import Annotated, Union, List
from os import getenv
from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from pydantic import BaseModel

app = FastAPI()

GPU_ENABLED = getenv("GPU_ENABLED", "False").lower() == "true"

# security = HTTPBasic()


class PostData(BaseModel):
    model_name: str = "llama-2-7b-chat.ggmlv3.q2_K"
    temperature: float = 0.1
    message: str
    max_tokens: int = 2000


def get_llm(data: PostData) -> LlamaCpp:
    # params: https://api.python.langchain.com/en/latest/llms/langchain.llms.llamacpp.LlamaCpp.html
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    params = {"temperature": data.temperature,
              "max_tokens": data.max_tokens,
              "top_p": 1
              }
    if GPU_ENABLED:
        # Change this value based on your model and your GPU VRAM pool.
        params['n_gpu_layers'] = 50
        # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
        params['n_batch'] = 512
    else:
        params['n_gpu_layers'] = 0
        params['n_batch'] = 1
    return LlamaCpp(
        model_path=f"./models/{data.model_name}.bin",
        **params,
        callback_manager=callback_manager,
        verbose=True,  # True
    )


async def get_answer(llm, messages) -> str:
    return llm(f"Question: {messages}")


@app.post("/chat/")
async def post_chat_prompt(data: PostData, llm: Annotated[LlamaCpp, Depends(get_llm)]) -> str:
    # callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    # llm = get_llm(data, callback_manager)
    print(f"Model: {data.model_name}, getting response...")
    results = await get_answer(llm, data.message)
    return results.replace("Answer:", "").replace("\n", "").strip()
