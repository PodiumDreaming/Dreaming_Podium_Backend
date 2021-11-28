from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.router import KaKao, Record, Images, Profile, Objective, Apple
from app.database import Tables
from app.database.conn import engine
import time
import logging


def init_app():
    """
    메인 함수 - 앱 실행
    :return:
    app
    """
    app = FastAPI()
    app.include_router(KaKao.router)
    app.include_router(Apple.router)
    # app.include_router(Training.router)
    # app.include_router(Conditioning.router)
    # app.include_router(Account.router)
    app.include_router(Profile.router)
    app.include_router(Objective.router)
    app.include_router(Record.router)
    app.include_router(Images.router)

    origins = [
        "http://localhost:3000",
        "localhost:3000"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    Tables.Base.metadata.create_all(bind=engine)
    return app


def init_logger():
    logger = logging.getLogger("FastAPI")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(filename="log/system.log")
    formatter = logging.Formatter(fmt="[%(asctime)s] %(name)s:%(levelname)s - %(message)s")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    return logger


app = init_app()
log = init_logger()


@app.middleware("http")
async def log_req(request: Request, call_next):
    start_time = time.time()
    method = request.method
    user = request.client.host
    port = request.client.port
    path = request.url.path
    scheme = request.url.scheme
    response = await call_next(request)

    process_time = start_time - time.time()
    process_time_f = f"{process_time:.3f}"
    status_code = response.status_code
    msg = f"{user}:{port} - [{method} {path} {scheme}] [{status_code}]: {process_time_f}"

    if status_code == 200:
        log.info(msg)
    elif status_code == 422 or status_code == 500:
        log.error(msg)
    else:
        log.info(msg)
    return response


@app.get("/")
def read_root():
    return {"hello": "world"}
