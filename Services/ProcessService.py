from .BaseService import BaseService
from .ProjectService import ProjectService
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from fastapi import UploadFile
from typing import List



class ProcessService(BaseService):
    def __init__(self,project_id:str):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectService().get_project_path(project_id)
    def get_file_extension(self, file_id: str):
        pass


    def get_file_loader(self, file_id: str):
        pass

    def get_file_content(self, file_id: str):
        pass

    def process_file_content(self, file_content: list, file_id: str,
                                                         chunk_size: int=100, overlap_size: int=20):

            pass
    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        pass



        