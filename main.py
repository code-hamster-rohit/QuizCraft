from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth.auth import Auth
import uvicorn

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

app.include_router(Auth().router, prefix='/auth', tags=['Auth'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)