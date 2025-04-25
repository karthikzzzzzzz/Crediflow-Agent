from dependency_injector import containers, providers
from Screening_ops_maker_agent.services.screening_ops import ScreeningOps


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Screening_ops_maker_agent.controllers.main",  
            "Screening_ops_maker_agent.kafka.listener",  
        ]
    )

    screening_service = providers.Singleton(ScreeningOps)
