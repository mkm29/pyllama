from typing import Any, Dict, List

from config import LlmConfig

from langchain.callbacks.manager import CallbackManager
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler, AsyncCallbackHandler
from langchain.llms import LlamaCpp
# from langchain.schema import AgentAction, AgentFinish, BaseMessage, LLMResult

# handler = StreamingStdOutCallbackHandler()
# async_handler = AsyncCallbackHandler()

def get_model(config: LlmConfig, handlers: List[Any]) -> LlamaCpp:
    """Get the LLM model."""
    return LlamaCpp(
        model_path=f"./models/{config.model_name}.bin",
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        top_p=config.top_p,
        n_gpu_layers=config.n_gpu_layers,
        n_batch=config.n_batch,
        callback_manager=CallbackManager(handlers),
        verbose=config.verbose,
    )