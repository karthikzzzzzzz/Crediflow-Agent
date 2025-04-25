from fastapi import HTTPException,APIRouter,Depends
from starlette import status
from utils.database import engine
from utils.database import get_db
from sqlalchemy.orm import Session
import utils.models as models
from Human_in_the_loop.services.hil import HumanInLoopAgent
from utils.schema import Request, AgentResponse
from dependency_injector.wiring import inject, Provide
from Human_in_the_loop.dependencies.containers import Container


hilagent= APIRouter()

models.Base.metadata.create_all(engine)

@hilagent.post("/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision", response_model= AgentResponse,summary="Process a chat query via human in the loop")
@inject
async def recieve_request(request:Request,realmId:str,userId:int,leadId:int, sessionId:str, hil: HumanInLoopAgent = Depends(Provide[Container.hil_service])):
    try:
        result = await hil.process_query(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))