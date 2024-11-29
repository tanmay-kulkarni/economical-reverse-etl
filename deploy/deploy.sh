#!/bin/bash

ENVIRONMENT=$1

if [[ ! $ENVIRONMENT =~ ^(dev|staging|prod)$ ]]; then
    echo "Usage: ./deploy.sh <dev|staging|prod>"
    exit 1
fi

# Check if config file exists
CONFIG_FILE="deploy/config/${ENVIRONMENT}.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file $CONFIG_FILE not found"
    exit 1
fi

# Install dependencies
pip install -r cdk/requirements.txt

# Deploy the stack
cd cdk
cdk deploy EtlStack${ENVIRONMENT^} --require-approval never