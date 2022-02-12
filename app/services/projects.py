from app.models.projects import Project
from app.services import db_client
from fastapi import HTTPException

class ProjectsService:
    async def create_project(self, project: Project):
        return await db_client.projects.insert_one(project.dict())

    async def get_project(self, project_id: str):
        project = await db_client.projects.find_one({"_id": project_id})
        if project:
            return project
        raise HTTPException(status_code=404, detail="Project not found")