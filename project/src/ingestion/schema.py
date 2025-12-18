from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class InputFeatures(BaseModel):
    url_length: int
    num_dots: int
    num_digits: int
    domain_age: int
    has_ip: int
    suspicious_keywords: int
    html_features: List[float]
    email_metadata: Dict[str, Any]
    tfidf_vector: List[float]
    embedding: List[float]

class PredictionOutput(BaseModel):
    probability: float
    prediction: int
    model_version: str

class Metadata(BaseModel):
    user_agent: str
    region: str
    referral: str
    time_of_day: str
    domain: str
    url: str
    hashed_text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    delayed_label: Optional[int] = None

class LogEntry(BaseModel):
    features: InputFeatures
    prediction: PredictionOutput
    metadata: Metadata
