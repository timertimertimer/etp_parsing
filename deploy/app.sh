#!/bin/sh

set -e

source .env

echo "Deploying app..."
playwright install

echo "App deployed!"