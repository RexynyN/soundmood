from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import route


app = FastAPI()

app.include_router(route.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def main():
    return { "message": "API Running :^)"}