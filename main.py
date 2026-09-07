from fastapi import FastAPI
from endpoints import router 
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from depends import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    try:
        yield
    finally:

        await close_db()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)