from fastapi import FastAPI
from .db import Base, engine
from .auth import router as auth_router

app = FastAPI(title="Notes API")

# Create tables on startup (simple dev approach; use Alembic in prod)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Welcome to the Notes API"}

# include auth routes
app.include_router(auth_router)
from .notes import router as notes_router
app.include_router(notes_router)
