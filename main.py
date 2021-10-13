from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import Account, Conditioning, Training


def init_app():
    """
    메인 함수 - 앱 실행
    :return:
    app
    """
    app = FastAPI()
    app.include_router(Account.router)
    app.include_router(Training.router)
    app.include_router(Conditioning.router)
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

    return app


app = init_app()


@app.get("/")
def read_root():
    return {"Hello": "World"}




