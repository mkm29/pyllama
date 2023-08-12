from typing import Union, List
from config import LlmConfig
from red_pandas import RedPandas
from llm import get_model

from langchain.llms import LlamaCpp
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

config: LlmConfig = None
# create buffer to hold new tokens
buffer: List[str] = []
red_pandas: RedPandas = None
model: LlamaCpp = None

handler = StreamingStdOutCallbackHandler()

def llm_start(serializers, prompts, **kwags) -> None:
    """Run when LLM starts running."""
    print(f'llm_start: {kwags}')
    # reinitialize buffer
    buffer.clear()

def new_token(token: str, **kwargs) -> None:
    """Run when a new token is generated."""
    # print(f'new_token: {kwargs}')
    # add token to buffer
    buffer.append(token)

def done(response, **kwargs):
    """Run when LLM is done running."""
    print(f'done: {kwargs}')
    # send buffer to red pandas
    print(''.join(buffer))

handler.on_llm_start = llm_start
handler.on_llm_end = done
handler.on_llm_new_token = new_token
handler.on_llm_error = lambda error, **kwargs: print('on_llm_error')



def init() -> Union[LlmConfig, RedPandas, LlamaCpp]:
    config = LlmConfig()
    red_pandas = RedPandas(config)
    model = get_model(config, [handler])
    return config, red_pandas, model


if __name__ == "__main__":
    config, red_pandas, model = init()
    print('PyLlama initialized')
    model("When was the last time that the Toronto Maples Leafs won the Stanley Cup?")
