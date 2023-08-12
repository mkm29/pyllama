from typing import Union, List
import re
from config import LlmConfig
from red_pandas import RedPandas
from llm import get_model
from utils import clean_strings

from langchain.llms import LlamaCpp
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

REGEX = re.compile(r"\d+\.")

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
    red_pandas.producer.flush()


def new_token(token: str, topic: str, **kwargs) -> None:
    """Run when a new token is generated."""
    # print(f'new_token: {token}')
    # add token to buffer

    # does token match REGEX
    if REGEX.match(token):
        return

    buffer.append(token)
    # test if token is a punctuation mark
    if token in [".", "!", "?"]:
        # if it is, add a newline to the buffer
        # clear buffer
        # send buffer to red pandas
        msg = clean_strings(buffer)
        print("Sening message: ", msg)
        # push to red pandas on a new thread
        buffer.clear()
        red_pandas.send_message(msg, topic)


def done(response, **kwargs):
    """Run when LLM is done running."""
    print(f"done: {kwargs}")
    # send buffer to red pandas
    # push remaining buffer to red pandas
    if len(buffer) > 0:
        msg = clean_strings(buffer)
        # push to red pandas on a new thread
        buffer.clear()
        print("Sening message: ", msg)
        red_pandas.send_message(msg, config.topic_name)


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
    promts = [
        "What is the meaning of life?",
        "What is the best programming language?",
        "When was the last time that the Toronto Maples Leafs won the Stanley Cup?"
    ]
    model(promts[0])
