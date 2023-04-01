FROM mambaorg/micromamba:1.4.1
USER root
ENV PYTHONPATH /root

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \ 
&& rm -rf /var/lib/apt/lists/*

COPY env.yaml /tmp/env.yaml
RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1

WORKDIR /root
COPY . /root
RUN pip install .


ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag