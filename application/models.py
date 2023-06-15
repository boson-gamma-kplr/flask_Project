from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
import json

# URL de connexion à la base de données ElephantSQL
# Assure-toi de remplacer "<username>", "<password>", "<host>" et "<database>" par tes propres informations de connexion
username = "igudfqsi"
password = "7SMOHysbUXXIU9yc0dFKVFM0TW5zTQQr"
host = "horton.db.elephantsql.com"
database = "igudfqsi"
url = f'postgresql://{username}:{password}@{host}/{database}'

# Création de l'instance engine
engine = create_engine(url)

# Création de l'instance Base
Base = declarative_base()

# Définition d'un modèle de table
class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)

    def __repr__(self):
        return f'{{"id":"{self.id}", "username":"{self.username}", "email":"{self.email}"}}'
    
# Création de la classe Session
Session = sessionmaker(bind=engine)

# Création de l'objet SESSION
session = Session()


class IncomeExpenses(Base):
    __tablename__ = 'api_sold'

    id = Column(Integer, primary_key=True)
    type = Column(String(30), default='income')
    date = Column(DateTime, default=func.now())
    amount = Column(Float, default=0.0)
    category = Column(String(30), default='misc')

    def __repr__(self):
        # return f"IncomeExpenses(id={self.id}, type={self.type})"
        return f'{{"id":"{self.id}", "date":"{self.date}", "type":"{self.type}", "category":"{self.category}", "amount":"{self.amount}"}}'
    
Base.metadata.create_all(engine)