FROM continuumio/miniconda3 AS base

WORKDIR /usr/local/app

COPY environment.yml ./
COPY shared ./shared

RUN conda env create -f environment.yml

FROM base AS api 

COPY api ./api
RUN chmod +x ./api/run.sh

CMD ["./api/run.sh"]

FROM base AS worker

COPY worker ./worker
RUN chmod +x ./worker/run.sh

CMD ["./worker/run.sh"]
