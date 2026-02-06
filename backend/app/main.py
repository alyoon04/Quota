from fastapi import FastAPI

app = FastAPI(title="Quota – Rate Limiter Platform")


@app.get("/health")
def health():
    return {"ok": True}
