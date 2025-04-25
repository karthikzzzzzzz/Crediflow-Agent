from dependency_injector import containers, providers
from Document_verification_agent.services.document_verification import DocumentVerification


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "Document_verification_agent.controllers.main",  
            "Document_verification_agent.kafka.listener",  
        ]
    )

    document_service = providers.Singleton(DocumentVerification)
