import databases
import orm
import sqlalchemy
from aiocache import caches

from starlette.applications import Starlette
from starlette.config import Config
from starlette.responses import UJSONResponse

# Configuration from environment variables or '.env' file.
config = Config(".env")

DATABASE_URL = config("DATABASE_URL")
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# You can use either classes or strings for referencing classes
caches.set_config({
    'default': {
        'cache': "aiocache.RedisCache",
        'endpoint': "127.0.0.1",
        'port': 6379,
        'timeout': 1,
        'serializer': {
            'class': "aiocache.serializers.JsonSerializer"
        },
        'plugins': [
            {'class': "aiocache.plugins.HitMissRatioPlugin"},
            {'class': "aiocache.plugins.TimingPlugin"}
        ]
    }
})
cache = caches.get('default')   # This always returns the SAME instance

app = Starlette(debug=config("DEBUG", default=False))


class Note(orm.Model):
    __tablename__ = "notes"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    text = orm.String(max_length=100)
    completed = orm.Boolean(default=False)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.route("/")
async def index(request):
    content = await cache.get("notes")
    if not content:
        notes = await Note.objects.all()
        content = [dict(note) for note in notes]
        await cache.set("notes", content)
    return UJSONResponse(content)


@app.route("/create")
async def create(request):
    note = await Note.objects.create(text="Hello", completed=False)
    return UJSONResponse(dict(note))
