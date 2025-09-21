FROM continuumio/miniconda3 AS base

WORKDIR /usr/local/app

COPY environment.yml ./
COPY shared ./shared

RUN conda env create -f environment.yml
RUN /opt/conda/envs/Online_Judge/bin/aerich init -t shared.settings.TORTOISE_ORM

FROM base AS api 

COPY api ./api

CMD ["/opt/conda/envs/Online_Judge/bin/uvicorn", "api.OJ-main:app", "--no-access-log"]

FROM base AS worker

COPY worker ./worker
