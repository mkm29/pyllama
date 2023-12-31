# pyLlama

This is a simple example of a self hosted LLM API, using Llama 2 7B-chat. More to follow.

## Pre-requisites

You need to have at least one model (eg. Llama 2 7B-chat). You can do so easily with:

```console
wget https://huggingface.co/localmodels/Llama-2-7B-Chat-ggml/resolve/main/llama-2-7b-chat.ggmlv3.q2_K.bin
```

## Build

Instead of coupling the model(s) with the Docker image (API), you should mount this in (either via Docker or Kubernetes). This allows you to update the model(s) without having to rebuild the image.

### Docker

I have included a multistage Docker build for convenience. You can build the image with:

```console
TAG=0.1.1
docker build -t smigula/pyllama:$TAG .
```

## Run

```console
docker run --mount type=bind,source="$(pwd)"/models,target=/models -p 8501:8501 smigula/pyllama:$TAG
```
