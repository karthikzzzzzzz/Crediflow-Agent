from dependency_injector import containers, providers
from Report_generation_agent.services.report_generation import ReportGeneration


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Report_generation_agent.controllers.main",  
            "Report_generation_agent.kafka.listener",  
        ]
    )

    report_service = providers.Singleton(ReportGeneration)
