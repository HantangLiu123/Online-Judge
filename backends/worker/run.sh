#!/bin/bash

if [ -f "./dbconfig/pyproject.toml" ]; then
    echo "migrating ..."
    /opt/conda/envs/Online_Judge/bin/aerich -c ./dbconfig/pyproject.toml migrate --name "auto"
    /opt/conda/envs/Online_Judge/bin/aerich -c ./dbconfig/pyproject.toml upgrade

else
    echo "initing ..."
    /opt/conda/envs/Online_Judge/bin/aerich -c ./dbconfig/pyproject.toml init -t shared.settings.TORTOISE_ORM
    /opt/conda/envs/Online_Judge/bin/aerich -c ./dbconfig/pyproject.toml init-db
fi

/opt/conda/envs/Online_Judge/bin/arq worker.worker-main.OJSettings --watch /usr/local/app/worker/utils
