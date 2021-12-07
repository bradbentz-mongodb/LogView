#!/usr/bin/env bash

if ! command -v black &> /dev/null
then
    echo "Code formatter not installed. Please run pip3 install black."
    exit
fi

black --line-length=120 -S . 
