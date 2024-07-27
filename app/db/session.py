from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

database_url = f"postgresql://postgres:{settings.database_password}@{settings.database_host}/{settings.database_name}"

engine = create_engine(database_url)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
