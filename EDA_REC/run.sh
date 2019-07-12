#!/bin/bash

docker run -itd --name devtest -p 8052:8052 --mount type=bind,source="$(pwd)/log",target=/mnt eda_rec:1.0

