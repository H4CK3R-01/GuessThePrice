__author__ = "Florian Kaiser"
__copyright__ = "Copyright 2022, GuessThePrice"
__credits__ = ["Florian Kaiser", "Florian Kellermann", "Linus Eickhof"]
__license__ = "GPL 3.0"
__version__ = "1.0.0"

import os

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

engine = create_engine(os.getenv("DATABASE_CONNECTION"))

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    telegram_id = Column(Integer, primary_key=True)
    username = Column(String(50))
    admin = Column(Boolean)

    def __repr__(self):
        return "<User(telegram_id='%s', username='%s', admin='%s')>" % (self.telegram_id, self.username, self.admin)


class Score(Base):
    __tablename__ = 'score'
    telegram_id = Column(Integer, ForeignKey('user.telegram_id'), primary_key=True)
    date = Column(DateTime, primary_key=True)
    product_id = Column(String(50), ForeignKey('product.product_id'))
    guess = Column(Float)
    score = Column(Integer)

    def __repr__(self):
        return "<Score(telegram_id='%s', date='%s', product_id='%s', guess='%s', score='%s')>" % (self.telegram_id, self.date, self.product_id, self.guess, self.score)


class Product(Base):
    __tablename__ = 'product'
    product_id = Column(String(50), primary_key=True)
    price = Column(Float)
    currency = Column(String(50))
    image_link = Column(String(5000))
    title = Column(String(5000))
    description = Column(String(5000))
    date = Column(DateTime)
    todays_product = Column(Boolean, default=False)

    def __repr__(self):
        return "<Product(product_id='%s', price='%s', image_link='%s', title='%s', description='%s', date='%s', todays_product='%s')>" % (
            self.product_id, self.price, self.image_link, self.title, self.description, self.date, self.todays_product)


# Create all tables by issuing CREATE TABLE commands to the DB.
Base.metadata.create_all(engine)

# Creates a new session to the database by using the engine we described.
Session = sessionmaker(bind=engine)
session = Session()
