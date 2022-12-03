#!/bin/bash
set -e

docker build -t algospace/{ALGORITHM_NAME}:{ALGORITHM_VERSION} -f algospace-dockerfile .
docker-compose -f algospace-docker-compose.yml up -d