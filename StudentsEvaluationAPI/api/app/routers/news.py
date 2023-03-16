from typing import Optional
from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, oauth2
from cloudinary.uploader import upload


router = APIRouter(tags=["News letter"], prefix="/newsletter")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.News)
async def create_news(
        news: schemas.PostNews, db: Session = Depends(database.get_db),
        admin: models.Admins = Depends(oauth2.get_admin_user),
        file: Optional[UploadFile] = None
):
    new_news = models.News(author_id=admin.id, **news.dict())
    if file:
        # delete the file from memory and rollover to disk to save unnecessary memory space
        file.file.rollover()
        file.file.flush()

        valid_types = [
            'image/png',
            'image/jpeg',
            'image/bmp',
        ]
        await utils.validate_file(file, 11000000, valid_types)
        pics = upload(file.file)
        url = pics.get("url")
        new_news.image = url

    db.add(new_news)
    db.commit()
    db.refresh(new_news)
    return new_news


@router.delete("/{newsID}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
        newsID: int, db: Session = Depends(database.get_db),
        admin: int = Depends(oauth2.get_admin_user)
):
    db.query(models.News).where(models.News.id == newsID).delete()
    db.commit()
    return


@router.get("/{newsID}", response_model=schemas.News)
async def get_news(
        newsID: int, db: Session = Depends(database.get_db),
):
    news = db.query(models.News).filter(models.News.id == newsID).all()
    return news


@router.put("/{newsID}/update", response_model=schemas.News)
async def update_news(
        newsID: int, news: schemas.UpdateNews, db: Session = Depends(database.get_db),
        admin: models.News = Depends(oauth2.get_admin_user),
        file: Optional[UploadFile] = None
):
    found_news = db.query(models.News).where(models.News.id == newsID).first()
    if file:
        # delete the file from memory and rollover to disk to save unnecessary memory space
        file.file.rollover()
        file.file.flush()

        valid_types = [
            'image/png',
            'image/jpeg',
            'image/bmp',
        ]
        await utils.validate_file(file, 11000000, valid_types)
        pics = upload(file.file)
        url = pics.get("url")
        found_news.image = url

    found_news.update(news)
    db.commit()
    db.refresh(found_news)
    return found_news
