from dependency_injector import containers, providers
from Langgraph.services.langgraph import Langgraph


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Langgraph.controllers.main",  
            "Langgraph.kafka.listener",  
        ]
    )

    langgraph_service = providers.Singleton(Langgraph)
