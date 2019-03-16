from starlette.applications import Starlette
from starlette.responses import UJSONResponse

from models import Note

app = Starlette(debug=True)


@app.route("/")
async def index(request):
    notes = await Note.objects.all()
    return UJSONResponse({"notes": [dict(note) for note in notes]})


@app.route("/create")
async def create(request):
    note = await Note.objects.create(text="Hello", completed=False)
    return UJSONResponse({"note": dict(note)})
