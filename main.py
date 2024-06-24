from fastapi import FastAPI
from routes.job import router as jd_router

app = FastAPI()

app.include_router(jd_router, prefix="/api/v1/jd", tags=["Job Descriptions"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)