#!/bin/sh

set -e

source .env

git pull origin main

deploy/rights.sh
