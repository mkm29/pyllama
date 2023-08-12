from typing import Union
from config import LlmConfig
from red_pandas import RedPandas
from llm import get_model

from langchain.llms import LlamaCpp
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

config: LlmConfig = None
red_pandas: RedPandas = None
model: LlamaCpp = None

def init() -> Union[LlmConfig, RedPandas, LlamaCpp]:
    config = LlmConfig()
    red_pandas = RedPandas(config)
    model = get_model(config, [StreamingStdOutCallbackHandler()])
    return config, red_pandas, model


if __name__ == "__main__":
    config, red_pandas, model = init()
    print(config)
