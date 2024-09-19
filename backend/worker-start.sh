#! /usr/bin/env bash
set -e

python /app/app/celeryworker_pre_start.py

celery -A app.core.celery worker -l info -Q main-queue -c 1 --loglevel=debug
