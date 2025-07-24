from app.v1_0.repositories import ProductoRepository
from app.v1_0.entities import ProductoDTO
from app.v1_0.models import Producto


class ProductoService:
    def __init__(self, repository: ProductoRepository):
        """
        Inicializa el servicio con un repositorio de productos.

        Args:
            repository (ProductoRepository): Repositorio que gestiona las operaciones con la base de datos.
        """
        self.repository = repository

    async def crear_producto(self, producto_dto: ProductoDTO) -> Producto:
        """
        Crea un nuevo producto si no existe otro con la misma referencia.

        Args:
            producto_dto (ProductoDTO): Datos del producto a crear.

        Returns:
            Producto: Producto creado exitosamente.

        Raises:
            ValueError: Si ya existe un producto con la misma referencia.
        """
        existente = await self.repository.get_by_referencia(producto_dto.referencia)
        if existente:
            raise ValueError("Ya existe un producto con esa referencia.")
        return await self.repository.create_producto(producto_dto)

    async def obtener_por_referencia(self, referencia: str) -> Producto | None:
        """
        Obtiene un producto por su referencia única.

        Args:
            referencia (str): Referencia del producto.

        Returns:
            Producto | None: Producto encontrado o None si no existe.
        """
        return await self.repository.get_by_referencia(referencia)

    async def obtener_por_descripcion(self, descripcion: str) -> list[Producto]:
        """
        Busca productos cuya descripción contenga una cadena dada.

        Args:
            descripcion (str): Parte o totalidad de la descripción.

        Returns:
            list[Producto]: Lista de productos coincidentes.
        """
        return await self.repository.get_by_descripcion(descripcion)

    async def actualizar_producto(self, producto_id: int, producto_dto: ProductoDTO) -> Producto | None:
        """
        Actualiza los datos de un producto existente.

        Args:
            producto_id (int): ID del producto a actualizar.
            producto_dto (ProductoDTO): Nuevos datos del producto.

        Returns:
            Producto | None: Producto actualizado o None si no se encontró.
        """
        return await self.repository.update_producto(producto_id, producto_dto)

    async def eliminar_producto(self, producto_id: int) -> bool:
        """
        Elimina un producto por su ID.

        Args:
            producto_id (int): ID del producto a eliminar.

        Returns:
            bool: True si se eliminó correctamente, False si no se encontró.
        """
        return await self.repository.delete_producto(producto_id)

    async def cambiar_estado(self, producto_id: int) -> Producto | None:
        """
        Cambia el estado de un producto (activo/inactivo).

        Args:
            producto_id (int): ID del producto.

        Returns:
            Producto | None: Producto actualizado o None si no existe.
        """
        return await self.repository.toggle_estado(producto_id)

    async def aumentar_stock(self, producto_id: int, cantidad: int) -> Producto | None:
        """
        Aumenta la cantidad disponible en inventario del producto.

        Args:
            producto_id (int): ID del producto.
            cantidad (int): Cantidad a aumentar (debe ser mayor a cero).

        Returns:
            Producto | None: Producto actualizado o None si no existe.

        Raises:
            ValueError: Si la cantidad es menor o igual a cero.
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        return await self.repository.aumentar_cantidad(producto_id, cantidad)

    async def disminuir_stock(self, producto_id: int, cantidad: int) -> Producto | None:
        """
        Disminuye la cantidad disponible en inventario del producto.

        Args:
            producto_id (int): ID del producto.
            cantidad (int): Cantidad a disminuir (debe ser mayor a cero).

        Returns:
            Producto | None: Producto actualizado o None si no existe o no hay stock suficiente.

        Raises:
            ValueError: Si la cantidad es inválida o el stock es insuficiente.
        """
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        producto = await self.repository.get_by_id(producto_id)
        if not producto:
            return None
        if (producto.cantidad or 0) < cantidad:
            raise ValueError("Stock insuficiente para realizar la operación.")
        return await self.repository.disminuir_cantidad(producto_id, cantidad)
