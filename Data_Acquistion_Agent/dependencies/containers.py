from dependency_injector import containers, providers
from Data_acquistion_agent.services.data_acquistion import DataAcquistion


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Data_acquistion_agent.controllers.main",  
            "Data_acquistion_agent.kafka.listener",  
        ]
    )

    data_acquisition_service = providers.Singleton(DataAcquistion)
