# database/models.py

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

# Создаем базовый класс для наших моделей (таблиц)
Base = declarative_base()

# --- Описание таблиц ---

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=True)
    full_name = Column(String)
    role = Column(String, default='participant') # participant, judge, admin
    access_code = Column(String, unique=True)

    # Связи
    works = relationship("Work", back_populates="participant")
    scores = relationship("Score", back_populates="judge")

class Nomination(Base):
    __tablename__ = 'nominations'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    # Связи
    works = relationship("Work", back_populates="nomination")

class Work(Base):
    __tablename__ = 'works'
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)

    participant_id = Column(Integer, ForeignKey('users.id'))
    nomination_id = Column(Integer, ForeignKey('nominations.id'))

    # Связи
    participant = relationship("User", back_populates="works")
    nomination = relationship("Nomination", back_populates="works")
    scores = relationship("Score", back_populates="work")

class Score(Base):
    __tablename__ = 'scores'
    id = Column(Integer, primary_key=True, index=True)
    
    work_id = Column(Integer, ForeignKey('works.id'))
    judge_id = Column(Integer, ForeignKey('users.id'))

    criteria_1 = Column(Integer) # Техника
    criteria_2 = Column(Integer) # Композиция
    criteria_3 = Column(Integer) # Оригинальность

    # Связи
    work = relationship("Work", back_populates="scores")
    judge = relationship("User", back_populates="scores")