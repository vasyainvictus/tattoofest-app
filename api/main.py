# api/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Импортируем из соседних файлов внутри пакета 'api'
from api.database import get_db, create_db_and_tables
from api.models import User as UserModel

create_db_and_tables()

class UserActivationRequest(BaseModel):
    telegram_id: int
    access_code: str

class UserResponse(BaseModel):
    telegram_id: int
    full_name: str
    role: str
    class Config:
        from_attributes = True

app = FastAPI()

# ЗАГЛУШКА ДЛЯ URL ФРОНТЕНДА
FRONTEND_URL = "https://tattoofest-app.vercel.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "*"], # "*" для простоты отладки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
def read_root():
    return {"message": "Бэкенд для тату-фестиваля работает!"}

@app.post("/api/activate_user", response_model=UserResponse)
def activate_user(request: UserActivationRequest, db: Session = Depends(get_db)):
    user_db = db.query(UserModel).filter(UserModel.access_code == request.access_code, UserModel.telegram_id == None).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Код неверный или уже использован")
    user_db.telegram_id = request.telegram_id
    db.commit()
    db.refresh(user_db)
    return user_db

@app.get("/api/users/by_telegram_id/{telegram_id}", response_model=UserResponse)
def get_user_by_telegram_id(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
@app.get("/api/fill_database_once")
def fill_database_once(db: Session = Depends(get_db)):
    from api.models import User, Nomination # Импортируем модели внутри функции

    # Проверяем, пустая ли база, чтобы не добавлять данные повторно
    if db.query(User).count() == 0:
        # Создаем тестовых пользователей
        judge1 = User(full_name="Судья Иван", role="judge", access_code="JUDGE-007")
        participant1 = User(full_name="Участник Петр", role="participant", access_code="PART-123")
        db.add_all([judge1, participant1])

        # Создаем тестовые номинации
        nomination1 = Nomination(name="Олдскул")
        nomination2 = Nomination(name="Лучшая черно-белая татуировка")
        db.add_all([nomination1, nomination2])
        
        db.commit()
        return {"status": "База данных успешно наполнена!"}
    
    return {"status": "База данных уже содержит данные."}
