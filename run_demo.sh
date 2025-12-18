#!/bin/bash

# Kill any existing processes on ports 8000 (API) and 8001 (Dashboard)
echo "Stopping existing services..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null
pkill -f "realtime_monitor.py"
pkill -f "demo_traffic.py"

# Set PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/project

echo "Starting Phishing Detection System..."

# 1. Start API (Background)
echo "1. Starting API..."
python project/src/ingestion/api.py > /dev/null 2>&1 &
API_PID=$!
sleep 2

# 2. Start Consumer (Background)
echo "2. Starting Consumer..."
python project/src/ingestion/consumer.py > /dev/null 2>&1 &
CONSUMER_PID=$!
sleep 2

# 3. Start Dashboard (Background)
echo "3. Starting Dashboard..."
python project/src/dashboard/app.py > /dev/null 2>&1 &
DASHBOARD_PID=$!
sleep 2

# 4. Start Monitor (Background)
echo "4. Starting Real-time Monitor..."
python project/scripts/realtime_monitor.py &
MONITOR_PID=$!
sleep 2

echo "------------------------------------------------"
echo "SYSTEM ONLINE"
echo "Dashboard: http://localhost:8001"
echo "API:       http://localhost:8000"
echo "------------------------------------------------"
echo "To stop everything, press Ctrl+C"

# 5. Interactive Loop
while true; do
    echo ""
    echo "------------------------------------------------"
    echo "OPTIONS:"
    echo "1. Run Traffic Simulation (Normal + Drift)"
    echo "2. Exit (Stops all services)"
    echo "------------------------------------------------"
    read -p "Enter choice [1-2]: " choice

    case $choice in
        1)
            echo "Running Traffic Simulation..."
            python project/scripts/demo_traffic.py
            ;;
        2)
            echo "Shutting down..."
            break
            ;;
        *)
            echo "Invalid option."
            ;;
    esac
done

# Cleanup on exit
kill $API_PID $CONSUMER_PID $DASHBOARD_PID $MONITOR_PID
