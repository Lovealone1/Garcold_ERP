from dependency_injector import containers, providers
from app.v1_0.v1_containers import APIContainer
from app.utils.database import async_session


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Contenedor principal que inyecta la sesión y registra módulos.
    """

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.v1_0.routers.venta_router",
            "app.v1_0.routers.compra_router"
            ]
    )

    db_session = providers.Object(async_session)

    api_container = providers.Container(
        APIContainer,
        db_session=db_session
    )
