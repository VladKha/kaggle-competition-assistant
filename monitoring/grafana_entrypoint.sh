#!/bin/bash

# Start Grafana in the background
/run.sh &

# Wait for Grafana to be ready
until curl -s http://localhost:3000/api/health | grep "ok"; do
    echo "Waiting for Grafana to be ready..."
    sleep 5
done

# Run the Python script to initialize the dashboard
python3 ./init_dashboard.py

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?