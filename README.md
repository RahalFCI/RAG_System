# RAG_System

# inside RAG_System dir  

pip install -r requiremnts.txt

alembic upgrade head   # only for first time 

alembic revision --autogenerate -m "fix vendor maps id column case"

uvicorn RAG_System.main:app --reload                                                                                                                 
                                 