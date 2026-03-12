from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


from RAG_System.helpers.Config import get_settings






app = FastAPI()

async def startup_span():
    settings = get_settings()
    connection = f"postgresql://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(connection)
    app.db_sessionmaker = sessionmaker(app.db_engine, expire_on_commit=False, class_=AsyncSession)


async def shutdown_span():
    await app.db_engine.dispose()

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)
     