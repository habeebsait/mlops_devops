# 1. Start Infrastructure (after Docker is running)
cd project/docker
docker-compose up -d

# 2. Go back to project root
cd ../..

# 3. Export PYTHONPATH (Critical Step!)
export PYTHONPATH=$PYTHONPATH:$(pwd)/project

# 4. Now run the components (in separate terminals, remember to export PYTHONPATH in each!)
# Terminal 1: API
export PYTHONPATH=$PYTHONPATH:$(pwd)/project
python project/src/ingestion/api.py

# Terminal 2: Consumer
export PYTHONPATH=$PYTHONPATH:$(pwd)/project
python project/src/ingestion/consumer.py

# Terminal 3: Demo Traffic
export PYTHONPATH=$PYTHONPATH:$(pwd)/project
python project/scripts/demo_traffic.py

#Terminal 4 (Realtime Monitor):
export PYTHONPATH=$PYTHONPATH:$(pwd)/project
python project/scripts/realtime_monitor.py



cd project/docker
docker-compose up -d kafka zookeeper