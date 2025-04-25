from dependency_injector import containers, providers
from Human_in_the_loop.services.hil import HumanInLoopAgent


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Human_in_the_loop.controllers.main",    
        ]
    )

    hil_service = providers.Singleton(HumanInLoopAgent)
