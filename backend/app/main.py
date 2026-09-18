from fastapi import FastAPI

app = FastAPI(title="Inventory Intel Agent")

@app.get("/health")
def health_check():
    return {"status": "ok"}
