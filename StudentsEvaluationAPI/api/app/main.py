from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, admins, guardians, results, students, news, teachers

app = FastAPI(debug=True)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(admins.router)
app.include_router(guardians.router)
app.include_router(results.router)
app.include_router(students.router)
app.include_router(news.router)
app.include_router(teachers.router)


@app.get("/")
async def root():
    return {"message": "Welcome to our Students Evaluation Performance system"}
