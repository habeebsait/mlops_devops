from fastapi import FastAPI, HTTPException, BackgroundTasks
from src.ingestion.schema import LogEntry, InputFeatures, PredictionOutput, Metadata
from src.ingestion.producer import PhishingLogProducer
import uvicorn
from datetime import datetime

app = FastAPI(title="Phishing Detection Monitoring API")
producer = PhishingLogProducer()

@app.post("/predict")
async def log_prediction(log: LogEntry, background_tasks: BackgroundTasks):
    """
    Endpoint to receive prediction logs and send them to Kafka.
    In a real scenario, this might also perform the prediction, 
    but here we assume the model is embedded or this is a sidecar.
    """
    try:
        background_tasks.add_task(producer.send_log, log)
        return {"status": "success", "message": "Log queued for processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown_event():
    producer.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
