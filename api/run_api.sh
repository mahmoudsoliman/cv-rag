#!/bin/bash

# Activate virtual environment and run the API
cd "$(dirname "$0")"
source .venv/bin/activate
python main.py
