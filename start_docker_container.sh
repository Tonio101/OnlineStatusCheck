#!/bin/bash

IMAGE_TAG=online_status
IMAGE_ID=$(docker images -q $IMAGE_TAG)

echo -n "Image ID: $IMAGE_ID"
#docker run -d --network=host --restart on-failure:5 ${IMAGE_ID}
docker run -d --network=host --name online_status --restart on-failure ${IMAGE_ID}
