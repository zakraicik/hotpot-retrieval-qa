from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hotpot_retrieval_qa.app.routes.health import router as health_check_router

app = FastAPI(title="Hotpot Retrieval QA API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_check_router)
