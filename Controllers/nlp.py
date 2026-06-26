import logging

from fastapi import APIRouter, HTTPException, Query, Request

from RAG_System.Services.NLPService import NLPController

logger = logging.getLogger(__name__)

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["nlp"],
)


def get_nlp_controller(request: Request) -> NLPController:
    return NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
        db_client=request.app.db_client,
    )


@nlp_router.post("/index-maps/{project_id}")
async def index_maps_data(
    request: Request,
    project_id: int,
    do_reset: bool = Query(False, description="Reset the collection before indexing"),
    top_n_reviews: int = Query(3, description="Maximum reviews to keep per entity"),
):
    try:
        controller = get_nlp_controller(request)
        result = await controller.build_and_index_maps_data(
            project_id=project_id,
            top_n_reviews=top_n_reviews,
            do_reset=do_reset,
        )
        return {
            "status": "success",
            "project_id": project_id,
            "indexed": bool(result),
        }
    except Exception as exc:
        logger.error("Error indexing maps data: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    
@nlp_router.post("/vectorize/{project_id}")
async def vectorize_project_data(
    request: Request,
    project_id: int,
):
    try:
        controller = get_nlp_controller(request)
        result = await controller.vectorize_project_data(project_id=project_id)
        return {
            "status": "success",
            "project_id": project_id,
            "vectorized": bool(result),
        }
    except Exception as exc:
        logger.error("Error vectorizing project data: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))



@nlp_router.post("/ask/{project_id}")
async def ask_rag_question(
    request: Request,
    project_id: int,
    query: str = Query(..., description="User question"),
    limit: int = Query(10, description="Maximum retrieved chunks"),
):
    try:
        controller = get_nlp_controller(request)
        project = await controller.ensure_project(project_id=project_id)
        answer, prompt, chat_history = await controller.answer_rag_question(
            project=project,
            query=query,
            limit=limit,
        )
        return {
            "status": "success",
            "project_id": project_id,
            "query": query,
            "answer": answer,
        }
    except Exception as exc:
        logger.error("Error answering RAG question: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
