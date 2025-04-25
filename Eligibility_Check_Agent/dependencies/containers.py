from dependency_injector import containers, providers
from Eligibility_check_agent.services.eligibility_check import EligibilityCheck


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Document_verification_agent.controllers.main",  
            "Document_verification_agent.kafka.listener",  
        ]
    )

    eligibility_service = providers.Singleton(EligibilityCheck)
