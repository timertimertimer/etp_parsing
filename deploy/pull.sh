#!/bin/sh

set -e

. .env

git pull origin main

deploy/rights.sh
