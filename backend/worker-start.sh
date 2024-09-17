#! /usr/bin/env bash
set -e

python /app/app/celeryworker_pre_start.py

celery -A app.api.task.celery_task.tasks worker -l info -Q main-queue -c 1
