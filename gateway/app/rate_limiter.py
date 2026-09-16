import redis
import os
from fastapi import HTTPException

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)

RATE_LIMIT = int(os.getenv("RATE_LIMIT", "10")) 

def check_rate_limit(client_ip: str):
    key = f"rate_limit:{client_ip}"
    current_requests = redis_client.get(key)
    
    if current_requests and int(current_requests) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too Many Requests - Rate Limit Excedido")
        
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, 60)
    pipe.execute()