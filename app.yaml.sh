#!/bin/bash
echo """
runtime: python312
env: standard

service: $GCLOUD_APP_SERVICE

env_variables:
  API_KEY: $API_KEY
  SEARCH_ENGINE_ID: $SEARCH_ENGINE_ID

entrypoint: gunicorn -b :8080 'src:create_app()'

instance_class: F1
"""
