from typing import Optional
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, oauth2


router = APIRouter(tags=["Students"], prefix="/student")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.Students)
async def create_student(
        user: schemas.StudentsCreate, parentID: Optional[int] = None,
        db: Session = Depends(database.get_db),
        role: models.Admins = Depends(oauth2.get_admin_user)
):
    hashed_pwd = utils.hashed(user.password)
    user.password = hashed_pwd
    new_user = models.Students(**user.dict())
    new_user.studentID = utils.generate_registration_number()

    teacher = db.query(models.Teacher).filter(models.Teacher.class_taught == user.student_class).first()
    if teacher:
        new_user.teacher_id = teacher.id

    if parentID:
        parent = db.query(models.Guardians).filter(models.Guardians.id == parentID).first()
        if parent:
            new_user.parent_id = parent.id

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.delete("/{userID}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
        userID: int, db: Session = Depends(database.get_db),
        user: models.Admins = Depends(oauth2.get_admin_user)
):
    db.query(models.Students).where(models.Students.id == userID).delete()
    db.commit()
    return

@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
        form_data: schemas.UpdatePassword,
        user: models.Admins = Depends(oauth2.get_current_user),
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
