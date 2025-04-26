from fastapi import FastAPI


agent = FastAPI()


@agent.post("/intelli-agent/v1/realms/{realmId}/users/{userId}/leads/{leadId}/session/{sessionId}/decision")
def chat(sessionId:str,userId:int,realId:str,leadId:int):
    pass
