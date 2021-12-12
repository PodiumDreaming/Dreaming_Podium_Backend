from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.router import KaKao, Record, Images, Profile, Objective, Apple
from app.database import Tables
from app.database.conn import engine
import time
import logging


def init_app(description):
    """
    메인 함수 - 앱 실행
    :return:
    app
    """
    app = FastAPI(
        title="Wright Backend",
        description=description,
        version="1.0.1",
        terms_of_service="https://blog.naver.com/PostView.naver?blogId=sujinju0311&logNo=222583009802&proxyReferer=",
        contact={
            "name": "Github",
            "url": "https://github.com/PodiumDreaming/Dreaming_Podium_Backend",
            "email": "jeongmh09@naver.com",
        },
        license_info={
            "name": "MIT License",
        },
    )
    app.include_router(KaKao.router)
    app.include_router(Apple.router)
    app.include_router(Profile.router)
    app.include_router(Objective.router)
    app.include_router(Record.router)
    app.include_router(Images.router)

    origins = [
        "http://localhost:3000",
        "localhost:3000",
        "http://localhost:3000"
        "localhost:8080",
        "http://localhost",
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
    """
    initialize logger for Request logging.
    :return: logger fot logging request and logger for logging error.
    """
    req_logger = logging.getLogger("Request")
    req_logger.setLevel(logging.INFO)
    err_logger = logging.getLogger("Error")
    err_logger.setLevel(logging.WARNING)

    req_handler = logging.FileHandler(filename="log/request.log")
    err_handler = logging.FileHandler(filename="log/error.log")

    formatter = logging.Formatter(fmt="[%(asctime)s] %(name)s:%(levelname)s - %(message)s")
    req_handler.setLevel(logging.INFO)
    req_handler.setFormatter(formatter)
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(formatter)

    req_logger.addHandler(req_handler)
    err_logger.addHandler(err_handler)
    return req_logger, err_logger


description = """
Wright API Server. 🚀

## KaKao

You can **Test Login with KaKao Account**.

## Apple

You can **Test Login with Apple Account**.

## Profile

You will be able to:

* **Create Profile**.
* **Read Profile**.
* **Update Profile**.

## Objective

You will be able to:

* **Create Objective**.
* **Read Objective**/
* **Update Objective**.

## Image Upload

You will be able to:

* **Upload Image to S3**.
* **Delete Image Url**.

## Record

You will be able to:

* **Create Record**.
* **Read Record**/
* **Read your API_Token**.
* **Test if your API_Token is valid.
"""
app = init_app(description=description)
req_log, err_log = init_logger()


@app.middleware("http")
async def log_req(request: Request, call_next):
    """
    Middleware that executes before and after request gets handled.
    :param request:
    :param call_next: Called API.
    :return:
    """
    # set log information
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

    if 200 <= status_code <= 300:
        # Record log.
        req_log.info(msg)
    elif status_code >= 400:
        # error is handled by exception handler
        pass
    else:
        req_log.info(msg)
    return response


@app.exception_handler(StarletteHTTPException)
async def leave_log(request: Request, exception):
    """
    Overriding exception handler to leave log.
    :param request:
    :param exception:
    :return:
    """
    # set log information
    method = request.method
    user = request.client.host
    port = request.client.port
    path = request.url.path
    scheme = request.url.scheme
    msg = f"{user}:{port} - [{method} {path} {scheme}] [{exception.status_code}]"
    # Record log.
    err_log.error(msg)
    return JSONResponse(status_code=exception.status_code,
                        content=exception.detail)


@app.get("/")
def read_root():
    return {"hello": "world"}
