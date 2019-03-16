import sqlalchemy

from models import database, metadata

# Create the database
engine = sqlalchemy.create_engine(str(database.url))
metadata.create_all(engine)
