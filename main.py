from fastapi import FastAPI
from routes.auth.auth import Auth
import uvicorn

app = FastAPI()

app.include_router(Auth().router, prefix='/auth', tags=['Auth'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)