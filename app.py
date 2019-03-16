import databases
import orm
import sqlalchemy
import typesystem

from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import UJSONResponse

# Configuration from environment variables or '.env' file.
config = Config(".env")

DATABASE_URL = config("DATABASE_URL")
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

app = Starlette(debug=config("DEBUG", default=False))


class Note(orm.Model):
    __tablename__ = "notes"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    text = orm.String(max_length=100)
    completed = orm.Boolean(default=False)


class NoteSchema(typesystem.Schema):
    text = typesystem.String()
    completed = typesystem.Boolean()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.route("/")
async def index(request):
    notes = await Note.objects.all()
    content = [dict(NoteSchema(dict(note))) for note in notes]
    return UJSONResponse(content)


@app.route("/create")
async def create(request):
    note = await Note.objects.create(text="Hello", completed=False)
    return UJSONResponse(dict(note))
