from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .Models.Vectordb.VectorDBFactory import VectorDBProviderFactory
from .Services.LLM.LLMProviderFactory import LLMProviderFactory
from .Services.LLM.Templates.template_parser import TemplateParser


from RAG_System.Controllers import base, data, nlp
from RAG_System.helpers.Config import get_settings






app = FastAPI()

async def startup_span():
    settings = get_settings()
    connection = f"postgresql://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(connection)
    app.db_sessionmaker = sessionmaker(app.db_engine, expire_on_commit=False, class_=AsyncSession)
    
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings, db_client=app.db_client)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    # vector db client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    await app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )


async def shutdown_span():
    await app.db_engine.dispose()

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)



app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)