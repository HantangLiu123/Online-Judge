#!/bin/bash

if psql -h db -U postgres -d mydb -tAc "SELECT to_regclass('public.aerich');" | grep -q aerich; then
    echo "Running migrations..."
    /opt/conda/envs/Online_Judge/bin/aerich upgrade
else
    echo "Initializing database..."
    /opt/conda/envs/Online_Judge/bin/aerich init-db
fi

/opt/conda/envs/Online_Judge/bin/uvicorn api.OJ-main:app --host 0.0.0.0 --port 8000 --reload --no-access-log
