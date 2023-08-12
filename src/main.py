from typing import Union, List
import threading
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
    print(f"llm_start: {kwags}")
    # reinitialize buffer
    buffer.clear()


def new_token(token: str, topic: str, **kwargs) -> None:
    """Run when a new token is generated."""
    # print(f'new_token: {kwargs}')
    # add token to buffer
    buffer.append(token)
    # if the buffer contains a newline, send it to red pandas
    if "\n" in buffer:
        # send buffer to red pandas
        thread = threading.Thread(
            target=red_pandas.send_message, args=("".join(buffer), topic)
        )
        thread.start()
        # clear buffer
        buffer.clear()


def done(response, **kwargs):
    """Run when LLM is done running."""
    print(f"done: {kwargs}")
    # send buffer to red pandas
    # push remaining buffer to red pandas
    if len(buffer) > 0:
        msg = "".join(buffer)
        # push to red pandas on a new thread
        thread = threading.Thread(
            target=red_pandas.send_message, args=(msg, config.topic_name)
        )
        thread.start()
        buffer.clear()


handler.on_llm_start = llm_start
handler.on_llm_end = done
handler.on_llm_new_token = lambda token, **kwargs: new_token(
    token, config.topic_name, **kwargs
)
handler.on_llm_error = lambda error, **kwargs: print("on_llm_error")


def init() -> Union[LlmConfig, RedPandas, LlamaCpp]:
    config = LlmConfig()
    config.topic_name = "llama7-1"
    red_pandas = RedPandas(config)

    model = get_model(config, [handler])
    return config, red_pandas, model


if __name__ == "__main__":
    config, red_pandas, model = init()
    print("PyLlama initialized")
    model("When was the last time that the Toronto Maples Leafs won the Stanley Cup?")
