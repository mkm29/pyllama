from typing import List
from pydantic import BaseSettings, Field


class LlmConfig(BaseSettings):
    num_paritions: int = Field(1, env="NUM_PARTITIONS")
    replication_factor: int = Field(1, env="REPLICATION_FACTOR")
    bootstrap_servers: List[str] = Field(["127.0.0.1"], env="BOOTSTRAP_SERVERS")
    gpu_enabled: bool = Field(False, env="GPU_ENABLED")
    model_name: str = Field("llama-2-7b-chat.ggmlv3.q2_K", env="MODEL_NAME")
    temperature: float = Field(0.1, env="TEMPERATURE")
    max_tokens: int = Field(2000, env="MAX_TOKENS")
    top_p: float = Field(1.0, env="TOP_P")
    n_gpu_layers: int = Field(1, env="N_GPU_LAYERS")
    n_batch: int = Field(1, env="N_BATCH")
    streaming: bool = Field(False, env="STREAMING")
    verbose: bool = Field(True, env="VERBOSE")
    topic_name: str = "general"
    broker_port: int = Field(42883, env="BROKER_PORT")

    class Config:
        env_prefix = ""
        case_sensitive = True
        # secrets_dir = './secrets'
        # env_file = '.env'
        # env_file_encoding = 'utf-8'
