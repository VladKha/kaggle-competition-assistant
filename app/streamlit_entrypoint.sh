#!/bin/bash

# Run the db and assistants initialization script
python storage_init.py

# Run the Streamlit app
exec streamlit run app.py