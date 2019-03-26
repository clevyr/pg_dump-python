#!/bin/bash

set -e

# Create a packaging staging area
rm -rf package
mkdir package
cp requirements.txt package/

# Use Docker, because Lambda is on Linux
docker run -v `pwd`/package:/package python:3.7 pip install --target /package -r /package/requirements.txt

# Create lambda.zip with packages
cd package
rm requirements.txt
zip -r9 ../lambda.zip .

# Add code to the zip
cd ../
zip -g lambda.zip main.py
zip -g -r lambda.zip bin/
rm -rf package