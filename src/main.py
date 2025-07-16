from fastapi import FastAPI

app = FastAPI(
    title="PosHub API",
    description="API for PosHub application",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "ok"} 