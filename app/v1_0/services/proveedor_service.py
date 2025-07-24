from app.v1_0.repositories.proveedor_repository import ProveedorRepository
from app.v1_0.entities import ProveedorDTO
from app.v1_0.models import Proveedor


class ProveedorService:
    def __init__(self, proveedor_repo: ProveedorRepository):
        """
        Servicio para manejar operaciones de negocio relacionadas con proveedores.

        Args:
            proveedor_repo (ProveedorRepository): Repositorio de acceso a datos para Proveedor.
        """
        self.proveedor_repo = proveedor_repo

    async def crear_proveedor(self, proveedor_dto: ProveedorDTO) -> Proveedor:
        """
        Crea un nuevo proveedor en el sistema.

        - Verifica que no exista un proveedor con el mismo número de identificación (cc_nit).
        - Valida que el celular contenga solo dígitos (si se proporciona).

        Args:
            proveedor_dto (ProveedorDTO): Datos del proveedor a crear.

        Returns:
            Proveedor: Proveedor creado.

        Raises:
            ValueError: Si el NIT ya existe o el celular no es válido.
        """
        existente = await self.proveedor_repo.get_by_cc_nit(proveedor_dto.cc_nit)
        if existente:
            raise ValueError(f"Ya existe un proveedor con NIT {proveedor_dto.cc_nit}")

        if proveedor_dto.celular and not proveedor_dto.celular.isdigit():
            raise ValueError("El número de celular debe contener solo dígitos")

        return await self.proveedor_repo.create_proveedor(proveedor_dto)

    async def actualizar_proveedor(self, proveedor_id: int, proveedor_dto: ProveedorDTO) -> Proveedor:
        """
        Actualiza los datos de un proveedor existente.

        Args:
            proveedor_id (int): ID del proveedor a actualizar.
            proveedor_dto (ProveedorDTO): Nuevos datos del proveedor.

        Returns:
            Proveedor: Proveedor actualizado.

        Raises:
            ValueError: Si el proveedor no existe.
        """
        proveedor = await self.proveedor_repo.get_by_id(proveedor_id)
        if not proveedor:
            raise ValueError("Proveedor no encontrado")

        return await self.proveedor_repo.update_proveedor(proveedor_id, proveedor_dto)

    async def eliminar_proveedor(self, proveedor_id: int) -> bool:
        """
        Elimina un proveedor por su ID.

        Args:
            proveedor_id (int): ID del proveedor a eliminar.

        Returns:
            bool: True si fue eliminado correctamente.

        Raises:
            ValueError: Si el proveedor no existe.
        """
        proveedor = await self.proveedor_repo.get_by_id(proveedor_id)
        if not proveedor:
            raise ValueError("Proveedor no encontrado")

        return await self.proveedor_repo.delete_proveedor(proveedor_id)

    async def obtener_por_cc_nit(self, cc_nit: str) -> Proveedor | None:
        """
        Obtiene un proveedor por su número de identificación (cc_nit).

        Args:
            cc_nit (str): Número de cédula o NIT del proveedor.

        Returns:
            Proveedor | None: Proveedor encontrado o None si no existe.
        """
        return await self.proveedor_repo.get_by_cc_nit(cc_nit)

    async def obtener_por_nombre(self, nombre: str) -> list[Proveedor]:
        """
        Busca proveedores cuyo nombre coincida parcialmente con el valor dado.

        Args:
            nombre (str): Nombre o fragmento del nombre a buscar.

        Returns:
            list[Proveedor]: Lista de proveedores que coinciden con el nombre.
        """
        return await self.proveedor_repo.get_by_nombre(nombre)
