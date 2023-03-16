from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, oauth2
from StudentsEvaluationAPI import __CLASSES__


router = APIRouter(tags=["Administrators"], prefix="/admin")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.Admin)
async def create_admin(
        user: schemas.AdministratorCreate, db: Session = Depends(database.get_db),
        role: str = Depends(oauth2.get_admin_user)
):
    hashed_pwd = utils.hashed(user.password)
    user.password = hashed_pwd
    new_user = models.Admins(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/teachers", response_model=list[schemas.Teacher])
async def get_all_teachers(
        db: Session = Depends(database.get_db),
        user: models.Admins = Depends(oauth2.get_admin_user)
):
    return db.query(models.Teacher).all()

@router.get("/students", response_model=list[schemas.Students])
async def get_all_students(
        db: Session = Depends(database.get_db),
        user: models.Admins = Depends(oauth2.get_admin_user)
):
    return db.query(models.Students).all()

@router.get("/get-classes", response_model=list[str])
async def get_all_classes(role: str = Depends(oauth2.get_admin_user)):
    return __CLASSES__

@router.get("/{member_class}/members", response_model=list[str])
async def get_class_members(
        member_class: str, db: Session = Depends(database.get_db),
        role: str = Depends(oauth2.get_admin_user)
):
    ret_val = []
    students = db.query(models.Students).filter(models.Students.student_class == member_class).all(),
    teachers = db.query(models.Teacher).filter(models.Teacher.class_taught == member_class).all()
    for teacher in teachers:
        if isinstance(teacher, list):
            for t in teacher:
                ret_val.append(t.name)
        else:
            ret_val.append(teacher.name)
    len_ret = len(ret_val)
    for student in students:
        if isinstance(student, list):
            for s in student:
                ret_val.append(s.lastname + " " + s.firstname)
        else:
            ret_val.append(student.lastname + " " + student.firstname)

    sub_ret_teacher = ret_val[:len_ret]
    sub_ret_student = ret_val[len_ret:]
    sub_ret_teacher = sorted(sub_ret_teacher)
    sub_ret_student = sorted(sub_ret_student)
    ret_val = sub_ret_teacher + sub_ret_student

    return ret_val

@router.get("/user-profile/{member}/{member_class}/{name}", response_model=schemas.Member)
async def get_user_profile(
        member_class: str, member: str, name: str,
        user: models.Admins = Depends(oauth2.get_admin_user),
        db: Session = Depends(database.get_db)
):
    ret_val = {}
    if member.strip() == "student":
        ret_val["Designation"] = "Student"
        students = db.query(models.Students).filter(
            (models.Students.lastname == name.strip().split(" ")[0]) and (models.Students.student_class == member_class)
        ).first()

        if not students:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{member} with name {name} not found")

        for key, value in students.__dict__.items():
            ret_val[key] = value

    elif member.strip() == "teacher":
        ret_val["Designation"] = "Teacher"
        teachers = db.query(models.Teacher).filter(
            (models.Teacher.name == name.strip()) and (models.Teacher.class_taught == member_class)
        ).first()

        if not teachers:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,  detail=f"{member} with name {name} not found")

        for k, v in teachers.__dict__.items():
            ret_val[k] = v

    return ret_val

