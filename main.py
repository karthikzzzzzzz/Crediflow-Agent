from fastapi import FastAPI
from Bank_Office_Agent.controllers.main import bankagent
from Document_Verification_Agent.controllers.main import documentagent
from Eligibility_Check_Agent.controllers.main import eligibilityagent
from Report_Generation_Agent.controllers.main import reportagent
from Screening_Ops_Maker_Agent.controllers.main import screeningagent
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Agents",
    description="This API routes requests to different agent.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bankagent,tags=["Bank-Office-Agent"])
app.include_router(documentagent,tags=["Document-Verification-Agent"])
app.include_router(eligibilityagent,tags=["Eligibility-Checker-Agent"])
app.include_router(reportagent,tags=["Report-Generation-Agent"])
app.include_router(screeningagent,tags=["Screening-OpsMaker-Agent"])
