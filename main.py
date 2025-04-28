from fastapi import FastAPI
from Back_office_agent.controllers.main import backagent
from Document_verification_agent.controllers.main import documentagent
from Eligibility_check_agent.controllers.main import eligibilityagent
from Report_generation_agent.controllers.main import reportagent
from Screening_ops_maker_agent.controllers.main import screeningagent
from fastapi.middleware.cors import CORSMiddleware
from Human_in_the_loop.controllers.main import hilagent
from Data_acquistion_agent.controllers.main import dataagent
from Data_acquistion_agent.dependencies.containers import Container as DataContainer
from Document_verification_agent.dependencies.containers import Container as DocContainer
from Eligibility_check_agent.dependencies.containers import Container as EligibilityContainer
from Report_generation_agent.dependencies.containers import Container as ReportContainer
from Screening_ops_maker_agent.dependencies.containers import Container as ScreeningContainer
from Human_in_the_loop.dependencies.containers import Container as HilContainer


data_container = DataContainer()
data_container.init_resources()
data_container.wire(modules=["Data_acquistion_agent.controllers.main"])

doc_container = DocContainer()
doc_container.init_resources()
doc_container.wire(modules=["Document_verification_agent.controllers.main"])

eligibility_container = EligibilityContainer()
eligibility_container.init_resources()
eligibility_container.wire(modules=["Eligibility_check_agent.controllers.main"])

report_container = ReportContainer()
report_container.init_resources()
report_container.wire(modules=["Report_generation_agent.controllers.main"])

screening_container = ScreeningContainer()
screening_container.init_resources()
screening_container.wire(modules=["Screening_ops_maker_agent.controllers.main"])

hil_container = HilContainer()
hil_container.init_resources()
hil_container.wire(modules=["Human_in_the_loop.controllers.main"])



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

app.include_router(backagent, prefix="/intelli-agent/back-office", tags=["Back Office Agent"])
app.include_router(dataagent, prefix="/intelli-agent/data-acquisition", tags=["Data Acquisition Agent"])
app.include_router(documentagent, prefix="/intelli-agent/document-verification", tags=["Document Verification Agent"])
app.include_router(eligibilityagent, prefix="/intelli-agent/eligibility-checker", tags=["Eligibility Checker Agent"])
app.include_router(reportagent, prefix="/intelli-agent/report-generation", tags=["Report Generation Agent"])
app.include_router(screeningagent, prefix="/intelli-agent/screening-ops", tags=["Screening Ops Maker Agent"])
app.include_router(hilagent, prefix="/intelli-agent/human-in-the-loop", tags=["Human in the Loop Agent"])
