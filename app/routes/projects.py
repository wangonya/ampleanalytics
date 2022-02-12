from fastapi import APIRouter, Depends, Security
from fastapi_auth0 import Auth0User

from app.models.projects import Project
from app.services.auth import auth
from app.services.projects import ProjectsService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("")
async def create_project(project: Project):
    return await ProjectsService().create_project(project)


@router.get(
    "",
    response_model=Project,
    dependencies=[Depends(auth.implicit_scheme)],
)
async def get_project(
    user: Auth0User = Security(auth.get_user),
):
    return await ProjectsService().get_project("123")
