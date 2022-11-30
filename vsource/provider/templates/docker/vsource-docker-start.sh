#!/bin/bash
set -e

docker build -t vsource/{ALGORITHM_NAME}:{ALGORITHM_VERSION} -f vsource-dockerfile .
docker-compose -f vsource-docker-compose.yml up -d