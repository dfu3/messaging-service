#!/bin/bash

set -e

echo "Starting the API..."
echo "Environment: ${ENV:-development}"

export FLASK_APP=app:create_app
export FLASK_ENV=${ENV:-development}
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000

export FLASK_DEBUG=1

flask run
echo "Application started successfully!" S