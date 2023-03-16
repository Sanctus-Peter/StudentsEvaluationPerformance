from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, oauth2


router = APIRouter(tags=["Guardians"], prefix="/guardian")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.Guardian)
async def create_guardian(
        user: schemas.GuardianCreate, db: Session = Depends(database.get_db),
        role: str = Depends(oauth2.get_admin_user)
):
    hashed_pwd = utils.hashed(user.password)
    user.password = hashed_pwd
    children = user.children_id
    del user.children_id
    new_user = models.Guardians(**user.dict())
    db.add(new_user)

    for _id in children:
        print(new_user.id)
        db.query(models.Students).filter(
            models.Students.studentID == _id
        ).update({"parent_id": new_user.id}, synchronize_session=False)
        db.commit()

    db.commit()
    db.refresh(new_user)
    return new_user

@router.delete("/{userID}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_guardian(
        userID: int, db: Session = Depends(database.get_db),
        role: str = Depends(oauth2.get_admin_user)
):
    db.query(models.Guardians).where(models.Guardians.id == userID).delete()
    db.commit()
    return

@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
        form_data: schemas.UpdatePassword,
        user: models.Guardians = Depends(oauth2.get_guardian),
        db: Session = Depends(database.get_db)
):
    if not utils.verify(form_data.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect password")
    if form_data.new_password != form_data.password:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Passwords do not match")
    user.update({"password": utils.hashed(form_data.new_password)}, synchronize_session=False)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}

@router.get("/", response_model=list[schemas.Guardian])
async def get_all_parents(
        db: Session = Depends(database.get_db),
        user: models.Admins = Depends(oauth2.get_admin_user)
):
    return db.query(models.Guardians).all()
