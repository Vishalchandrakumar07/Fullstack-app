from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, workouts
from .database import Base, engine


app = FastAPI()

Base.metadata.create_all(bind=engine)

# Add CORS middleware to allow requests from localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with the correct frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Health check route
@app.get("/")
def health_check():
    return "Health check complete"


app.include_router(auth.router)
app.include_router(workouts.router)
