from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL de connexion à la base de données ElephantSQL
# Assure-toi de remplacer "<username>", "<password>", "<host>" et "<database>" par tes propres informations de connexion
username = ""
password = ""
host = ""
database = ""
url = f'postgresql://{username}:{password}@{host}/{database}'

# Création de l'instance engine
engine = create_engine(url)

# Création de l'instance Base
Base = declarative_base()

# Définition d'un modèle de table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)

    def __repr__(self):
        return f'User(id={self.id}, username={self.username}, email={self.email})'
    
# Création de la classe Session
Session = sessionmaker(bind=engine)

# Création de l'objet SESSION
SESSION = Session()


class IncomeExpenses(Base):
    __tablename__ = 'api_sold'

    id = Column(Integer, primary_key=True)
    type = Column(String(30), default='income')
    # amount = Column(Float)
    # date = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"IncomeExpenses(id={self.id}, type={self.type})"
        # return f"IncomeExpenses(id={self.id}, type={self.type}, amount={self.amount}, date={self.date})"