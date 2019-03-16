from starlette.applications import Starlette
from starlette.responses import UJSONResponse


app = Starlette(debug=True)


@app.route('/')
async def index(request):
    print(request)
    return UJSONResponse(content={'hello': 'world'})