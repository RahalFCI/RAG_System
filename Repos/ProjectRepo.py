
import logging 
from sqlalchemy import func, select

from RAG_System.Models.project import Project

from .BaseRepo import BaseRepo



class projectRepo(BaseRepo):
    def __init__(self, db_client):
        super().__init__(db_client = db_client)
        self.db_client = db_client
        self.logger = logging.getLogger("uvicorn")
    
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance
    async def create_project(self, project:Project):
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        return project

        
    async def get_project_or_create_one(self, project_id: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()
                if project is None:
                    self.logger.info(f"Queried for project_id {project_id}, not found and we created it ")
                    project_rec = Project(
                        project_id = project_id
                    )

                    project = await self.create_project(project=project_rec)
                    return project
                else:
                    return project
    async def get_all_projects(self,page : int=1, page_size : int = 10 ):
        async with self.db_client() as session:
            async with session.begin():
                total_records = await session.execute(select(func.count(Project.project_id)))
                total_records = total_records.scalar()
                total_pages = total_records // page_size + (1 if total_records % page_size > 0 else 0)
                offset = (page - 1) * page_size
                query = select(Project).offset(offset).limit(page_size)
                result = await session.execute(query)
                projects = result.scalars().all()
                return projects, total_pages