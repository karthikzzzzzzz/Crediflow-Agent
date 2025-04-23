from fastapi import HTTPException,APIRouter,Depends
from starlette import status
from config.database import engine
from config.database import get_db
from sqlalchemy.orm import Session
from config.models import Logs
import config.models as models
from Human_in_the_loop.services.hil import hil
from config.schema import Request


hilagent= APIRouter()

models.Base.metadata.create_all(engine)

@hilagent.post('/hil/api/v1/request')
async def recieve_request(request:Request):
    try:
        result = await hil.process_query(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))