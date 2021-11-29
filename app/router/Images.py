from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Header, status
from typing import List
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database import crud
from app.database.conn import get_db, get_s3
from app.config.config import BUCKET_NAME
from app.database.Models import Profile
from datetime import datetime
from ..util import convert_date, token_verification


router = APIRouter(
    prefix="/images",
    tags=["이미지 업로드"],
    dependencies=[],
)


@router.post("/uploadfile")
async def upload_img(user_id: str, image_type: str, wdate,
                     files: List[UploadFile] = File(...), db: Session = Depends(get_db), s3=Depends(get_s3),
                     token=Header(None, title="API_Token")):
    """
    API to upload image files for profile or record.\n
    :param user_id: user_id of image owner.\n
    :param image_type:\n
        "profile" for profile image\n
        "success" or "failure" for training record image.\n
    :param wdate: written date of record. If uploading profile image, enter today's date.\n
    e.g) Fri Nov 19 2021\n
    :param files: Uploading image files.\n
    :param db: db connection. This field is not required.\n
    :param s3: s3 connection. This field is not required.\n
    :param token: API_Token you received when you registered in.\n
    :return: 200ok on success.\n
    """
    if not token_verification(token=token, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )
    if image_type not in ["profile", "success", "failure"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image_type",
        )
    else:
        image_urls = []
        log = {}
        for i in range(len(files)):
            # meta data of file
            content = await files[i].read()
            name = files[i].filename
            path = os.path.join("./temp/", name)
            content_type = files[i].content_type

            # temporary save
            with open(path, "wb") as fp:
                fp.write(content)

            try:
                # upload file to s3 bucket
                now = datetime.now().strftime("%Y%m%d%H%M%S")
                key = f"{image_type}_image/{user_id}_{now}{i}_{name}"
                s3.upload_file(path, Bucket=BUCKET_NAME, Key=key, ExtraArgs={"ContentType": content_type})
                url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{key}"

                # add url to list
                image_urls.append(url)

                # delete file in temporary directory.
                os.remove(path)

                # DB update operation

                if image_type == "profile":
                    old_profile = crud.read_profile(db=db, user_id=user_id)
                    if old_profile:
                        new_profile = Profile(user_id=user_id,
                                              name=old_profile.name,
                                              gender=old_profile.gender,
                                              birthday=old_profile.birthday,
                                              team=old_profile.team,
                                              field=old_profile.field,
                                              profile_image=image_urls[0])
                        crud.update_profile(db=db, profile=new_profile)
                        log.update({f"file_{i}": "Success"})
                    else:
                        new_profile = Profile(user_id=user_id,
                                              profile_image=image_urls[0])
                        crud.create_profile(db=db, profile=new_profile)
                        log.update({f"file_{i}": "Success"})
                    break
                else:
                    d = convert_date(wdate).get("date")
                    old_tr = crud.read_tr(db=db, user_id=user_id, wdate=d, number=1)[0]
                    tr_content = old_tr.content
                    if image_type == "success":
                        success = tr_content.get("success").get("content")
                        tr_content["success"] = {"content": success, "image": image_urls}
                    else:
                        failure = tr_content.get("failure").get("content")
                        tr_content["failure"] = {"content": failure, "image": image_urls}
                    crud.update_tr(db=db, user_id=user_id, wdate=d, content=tr_content, feedback=old_tr.feedback)
                    log.update({f"file_{i}": "Success"})

            except SQLAlchemyError as sql:
                print(sql)
                log.update({f"file_{i}": "Failed"})
                continue

            except Exception as e:
                print(e)
                log.update({f"file_{i}": "Failed"})
                continue

    return {"Status": "200 OK",
            "Detail": log}


@router.post("/delete-record-image")
async def delete_image(user_id: str, db=Depends(get_db), token=Header(None, title="API_Token")):
    """
    API to remove image-url of success/failure images of training record.
    :param user_id:
    :param db:
    :param token: API_Token you received when you registered in.\n
    :return:
    """
    if not token_verification(token=token, user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )
