import databases
import orm
import sentry_sdk
import sqlalchemy
import typesystem
from orm.exceptions import NoMatch
from sentry_asgi import SentryMiddleware
from starlette.applications import Starlette
from starlette.config import Config
from starlette.endpoints import HTTPEndpoint
from starlette.responses import UJSONResponse

# Configuration from environment variables or '.env' file.
config = Config(".env")

DATABASE_URL = config("DATABASE_URL")
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

sentry_sdk.init(dsn=config("SENTRY_DSN"))

app = Starlette(debug=config("DEBUG", default=False))
app.add_middleware(SentryMiddleware)


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


@app.route("/note/{id}")
class NoteEndpoint(HTTPEndpoint):
    async def get(self, request):
        try:
            note = await Note.objects.get(id=request.path_params.get("id"))
            return UJSONResponse(dict(NoteSchema(note)))
        except NoMatch:
            return UJSONResponse({"error": "not found"}, status_code=404)

    async def post(self, request):
        note = await Note.objects.create(text="Hello", completed=False)
        return UJSONResponse(dict(note))

    async def delete(self, request):
        try:
            note = await Note.objects.get(id=request.path_params.get("id"))
            await note.delete()
            return UJSONResponse({'success': True})
        except NoMatch:
            return UJSONResponse({"error": "not found"}, status_code=404)


@app.route("/sentry/")
def homepage(request):
    raise ValueError("nope")


@app.exception_handler(404)
async def not_found(request, exc):
    return UJSONResponse(content={"error": "not found"}, status_code=exc.status_code)


@app.exception_handler(500)
async def server_error(request, exc):
    return UJSONResponse(
        content={"error": "something goes wrong"}, status_code=exc.status_code
    )
