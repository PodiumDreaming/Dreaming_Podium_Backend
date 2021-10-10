from fastapi import FastAPI
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
    return app


app = init_app()


@app.get("/")
def read_root():
    return {"Hello": "World"}




