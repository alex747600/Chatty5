from fastapi import FastAPI
from app.routers import users, content, logs, stats, activity
from app.utils import init_sentry

init_sentry()

app = FastAPI(title="Admin Service", version="1.0.0")

app.include_router(users.router)
app.include_router(content.router)
app.include_router(logs.router)
app.include_router(stats.router)
app.include_router(activity.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}