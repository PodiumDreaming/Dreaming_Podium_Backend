from fastapi import FastAPI, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.router import KaKao, Conditioning, Training, Account
from app.database import Tables, crud
from app.database.conn import engine, get_db

from PIL import Image
from io import BytesIO
from sqlalchemy.orm import Session
import urllib.request

saveno = 1


def init_app():
    """
    메인 함수 - 앱 실행
    :return:
    app
    """
    app = FastAPI()
    app.include_router(KaKao.router)
    app.include_router(Training.router)
    app.include_router(Conditioning.router)
    app.include_router(Account.router)
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


app = init_app()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/image_test")
async def show_img(db: Session = Depends(get_db)):
    img = Image.open("C:/Users/jeong/PycharmProjects/너굴맨.jpg")
    # img.show()
    buf = BytesIO()
    img.save(buf, format="JPEG")
    name = img.filename
    data = buf.getvalue()

    crud.save_img(db, name, data)
    return {"Image type:": type(img)}


@app.get("/read_img")
async def read_img(db: Session = Depends(get_db)):
    img_data = crud.read_img(db).img_data
    img = Image.open(BytesIO(img_data))
    img.show()


@app.get("/url_test")
async def show_img():
    global saveno
    urllib.request.urlretrieve(
        "https://libapps-au.s3-ap-southeast-2.amazonaws.com/accounts/120707/images/KHU_Wordmark.png",
        f"{saveno}.jpg"
    )

    img = Image.open(f"{saveno}.jpg")
    saveno += 1
    img.show()


@app.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    name = file.filename
    crud.save_img(db, name, content)

