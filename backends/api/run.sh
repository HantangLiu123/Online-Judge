#!/bin/bash

/opt/conda/envs/Online_Judge/bin/uvicorn api.OJ-main:app --host 0.0.0.0 --port 8000 --reload --no-access-log
