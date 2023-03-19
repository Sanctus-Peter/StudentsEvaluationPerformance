from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from StudentsEvaluationAPI import __SUBJECT_LISTS__, __CLASSES__
from fastapi import HTTPException, status


class Subject(str):
    __subject_list__ = __SUBJECT_LISTS__

    def __new__(cls, value):
        if value not in cls.__subject_list__:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"{value} is not a valid subject"
            )
        return str.__new__(cls, value)


class Classes(str):
    __classes_list__ = __CLASSES__

    def __new__(cls, value):
        if value not in cls.__classes_list__:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"{value} is not a valid student class"
            )
        return str.__new__(cls, value)


class StudentsBase(BaseModel):
    firstname: str
    lastname: str
    middlename: Optional[str]
    email: EmailStr


class StudentsCreate(StudentsBase):
    password: str
    gender: str
    address: str
    student_class: Classes


class StudentsUpdate(BaseModel):
    firstname: Optional[str]
    lastname: Optional[str]
    middlename: Optional[str]
    email: Optional[EmailStr]
    gender: Optional[str]
    address: Optional[str]
    student_class: Optional[Classes]


class Students(StudentsBase):
    id: int
    student_id: str
    student_class: Classes

    class Config:
        orm_mode = True


class Member(BaseModel):
    id: int
    Designation: str
    title: Optional[str] = ""
    name: Optional[str] = ""
    lastname: Optional[str] = ""
    firstname: Optional[str] = ""
    middlename: Optional[str] = ""
    gender: str
    address: str
    student_class: Optional[Classes] = ""
    class_taught: Optional[Classes] = ""
    reg_date: date


class TeacherBase(BaseModel):
    title: str
    name: str
    email: EmailStr


class TeacherCreate(TeacherBase):
    gender: str
    address: str
    mobile_no: str
    class_taught: Optional[Classes]
    subject_taught: Optional[List[Subject]]
    password: str


class TeacherUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    gender: Optional[str]
    address: Optional[str]
    mobile_no: Optional[str]
    class_taught: Optional[Classes]


class Teacher(TeacherBase):
    id: int
    class_taught: Optional[str]

    class Config:
        orm_mode = True


class UpdatePassword(BaseModel):
    old_password: str
    new_password: str
    password: str


class AdminBase(BaseModel):
    name: str
    email: EmailStr


class AdministratorCreate(AdminBase):
    password: str


class AdministratorUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]


class Admin(AdminBase):
    id: int

    class Config:
        orm_mode = True


class Administrator(AdminBase):
    id: int
    students: list[Students] = []

    class Config:
        orm_mode = True


class GuardianBase(BaseModel):
    title: str
    name: str
    email: EmailStr


class GuardianCreate(GuardianBase):
    password: str
    gender: str
    address: str
    mobile_no: str
    children_id: list[str]


class Guardian(GuardianBase):
    id: int

    class Config:
        orm_mode = True


class Parent(GuardianBase):
    id: int
    children: list[Students]

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    id: int
    name: str
    access_token: str
    token_type: str = "bearer"


class TokData(BaseModel):
    id: Optional[str] = None


class NewsBase(BaseModel):
    title: str
    content: str
    category: str


class PostNews(NewsBase):
    pass


class UpdateNews(BaseModel):
    title: Optional[str]
    content: Optional[str]
    category: Optional[str]


class News(PostNews):
    id: int
    date: datetime
    image: Optional[str]
    owner: Admin

    class Config:
        orm_mode = True
