from fastapi import APIRouter, Depends, File, UploadFile
from PIL import Image
from io import BytesIO
from typing import List
import os
from sqlalchemy.orm import Session
from app.database import Tables, crud
from app.database.conn import get_db, get_s3
from app.config.config import BUCKET_NAME
from app.database.Models import Profile
from datetime import date, datetime
from app.router.Record import convert_date
import urllib.request

router = APIRouter(
    prefix="/test",
    tags=["기능테스트용"],
    dependencies=[],
)

saveno = 1


@router.get("/image_test")
async def show_img(db: Session = Depends(get_db)):
    img = Image.open("C:/Users/jeong/PycharmProjects/너굴맨.jpg")
    # img.show()
    buf = BytesIO()
    img.save(buf, format="JPEG")
    name = img.filename
    data = buf.getvalue()

    crud.save_img(db, name, data)
    return {"Image type:": type(img)}


@router.get("/url_test")
async def show_img():
    global saveno
    urllib.request.urlretrieve(
        "https://libapps-au.s3-ap-southeast-2.amazonaws.com/accounts/120707/images/KHU_Wordmark.png",
        f"{saveno}.jpg"
    )

    img = Image.open(f"{saveno}.jpg")
    saveno += 1
    img.show()


@router.get("/read_img")
async def read_img(db: Session = Depends(get_db)):
    img_data = crud.read_img(db).img_data
    img = Image.open(BytesIO(img_data))
    img.show()


@router.post("/uploadfile")
async def upload_img(user_id: str, image_type: str, wdate,
                     files: List[UploadFile] = File(...), db: Session = Depends(get_db), s3=Depends(get_s3)):
    if image_type not in ["profile", "success", "failure"]:
        return
    else:
        image_urls = {}
        for i in range(len(files)):
            # meta data of file
            content = await files[i].read()
            name = files[i].filename
            path = os.path.join("./temp/", name)
            content_type = files[i].content_type

            # temporary save
            with open(path, "wb") as fp:
                fp.write(content)
            fp.close()

            # upload file to s3 bucket
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            key = f"{image_type}_image/{user_id}_{now}{i}_{name}"
            s3.upload_file(path, Bucket=BUCKET_NAME, Key=key, ExtraArgs={"ContentType": content_type})
            url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{key}"

            # add url to dict
            image_key = f"image{i}"
            image_urls.update({image_key: url})

            # delete file in temporary directory.
            os.remove(path)

            # DB update operation
            if image_type == "profile":
                old_profile = crud.read_profile(db=db, user_id=user_id)
                new_profile = Profile(user_id=user_id,
                                      name=old_profile.name,
                                      gender=old_profile.gender,
                                      birthday=old_profile.birthday,
                                      team=old_profile.team,
                                      field=old_profile.field,
                                      profile_image=image_urls)
                crud.update_profile(db=db, profile=new_profile)
            else:
                d = convert_date(wdate).get("date")
                old_tr = crud.read_tr(db=db, user_id=user_id, wdate=d, number=1)[0]
                tr_content = old_tr.content
                success = tr_content.get("success").get("content")
                tr_content["success"] = {"content": success, "image": image_urls}
                crud.update_tr(db=db, user_id=user_id, wdate=d, content=tr_content, feedback=old_tr.feedback)

    return {"status": "200"}
