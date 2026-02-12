from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    # 환경 변수를 통해 어떤 환경(Dev/Prod)인지 출력
    env = os.getenv("APP_ENV", "local")
    return {"Hello": "World", "Environment": env}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}