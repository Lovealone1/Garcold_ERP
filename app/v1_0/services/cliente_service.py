from app.v1_0.repositories.cliente_repository import ClienteRepository
from app.v1_0.entities import ClienteDTO
from app.v1_0.models import Cliente


class ClienteService:
    def __init__(self, cliente_repository: ClienteRepository):
        """
        Servicio para manejar operaciones de negocio relacionadas con clientes.

        Args:
            cliente_repository (ClienteRepository): Repositorio de acceso a datos para Cliente.
        """
        self.cliente_repository = cliente_repository

    async def crear_cliente(self, cliente_dto: ClienteDTO) -> Cliente:
        """
        Crea un nuevo cliente en el sistema.

        - Verifica que no exista un cliente con el mismo número de identificación (cc_nit).
        - Valida que el celular contenga solo dígitos (si es proporcionado).
        - Asigna un saldo de 0.0 por defecto si no se especifica.

        Args:
            cliente_dto (ClienteDTO): Datos del cliente a crear.

        Returns:
            Cliente: Cliente creado.

        Raises:
            ValueError: Si el NIT ya existe o si el celular tiene caracteres inválidos.
        """
        existente = await self.cliente_repository.get_by_cc_nit(cliente_dto.cc_nit)
        if existente:
            raise ValueError(f"Ya existe un cliente con NIT {cliente_dto.cc_nit}")

        if cliente_dto.celular and not cliente_dto.celular.isdigit():
            raise ValueError("El número de celular debe contener solo dígitos")

        cliente_dto.saldo = cliente_dto.saldo or 0.0

        return await self.cliente_repository.create_cliente(cliente_dto)

    async def actualizar_cliente(self, cliente_id: int, cliente_dto: ClienteDTO) -> Cliente:
        """
        Actualiza los datos de un cliente existente.

        Args:
            cliente_id (int): ID del cliente a actualizar.
            cliente_dto (ClienteDTO): Nuevos datos del cliente.

        Returns:
            Cliente: Cliente actualizado.

        Raises:
            ValueError: Si el cliente no existe.
        """
        cliente = await self.cliente_repository.get_by_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado")

        return await self.cliente_repository.update_cliente(cliente_id, cliente_dto)

    async def eliminar_cliente(self, cliente_id: int) -> bool:
        """
        Elimina un cliente por su ID.

        Args:
            cliente_id (int): ID del cliente a eliminar.

        Returns:
            bool: True si fue eliminado, False si no se encontró.

        Raises:
            ValueError: Si el cliente no existe.
        """
        cliente = await self.cliente_repository.get_by_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado")

        return await self.cliente_repository.delete_cliente(cliente_id)

    async def obtener_por_cc_nit(self, cc_nit: str) -> Cliente | None:
        """
        Obtiene un cliente por su número de identificación (cc_nit).

        Args:
            cc_nit (str): Número de cédula o NIT del cliente.

        Returns:
            Cliente | None: Cliente encontrado o None si no existe.
        """
        return await self.cliente_repository.get_by_cc_nit(cc_nit)

    async def obtener_por_nombre(self, nombre: str) -> list[Cliente]:
        """
        Busca clientes cuyo nombre coincida parcialmente con el valor dado.

        Args:
            nombre (str): Nombre o fragmento del nombre a buscar.

        Returns:
            list[Cliente]: Lista de clientes que coinciden con el nombre.
        """
        return await self.cliente_repository.get_by_nombre(nombre)
