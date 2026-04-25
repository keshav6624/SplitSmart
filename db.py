from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///data/app.db", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Space(Base):
    __tablename__ = "spaces"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    space_id = Column(Integer)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    title = Column(String)  # ✅ NEW FIELD
    amount = Column(Float)
    space_id = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)

class ExpenseSplit(Base):
    __tablename__ = "expense_splits"
    id = Column(Integer, primary_key=True)
    expense_id = Column(Integer)
    member_name = Column(String)
    amount = Column(Float)

def init_db():
    Base.metadata.create_all(engine)