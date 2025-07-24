from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.v1_0.models import Cliente
from app.v1_0.repositories import BaseRepository
from app.v1_0.entities import ClienteDTO

class ClienteRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(Cliente, db)

    async def create_cliente(self, cliente_dto: ClienteDTO) -> Cliente:
        cliente = Cliente(**cliente_dto.model_dump())
        return await self.create(cliente)

    async def get_by_cc_nit(self, cc_nit: str) -> Cliente | None:
        result = await self.db.execute(
            select(Cliente).where(Cliente.cc_nit == str(cc_nit))
        )
        return result.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str) -> list[Cliente]:
        result = await self.db.execute(
            select(Cliente).where(Cliente.nombre.ilike(f"%{nombre}%"))
        )
        return result.scalars().all()

    async def update_cliente(self, cliente_id: int, cliente_dto: ClienteDTO) -> Cliente | None:
        cliente = await self.get_by_id(cliente_id)
        if cliente:
            for field, value in cliente_dto.model_dump(exclude_unset=True).items():
                setattr(cliente, field, value)
            await self.db.commit()
            await self.db.refresh(cliente)
            return cliente
        return None

    async def update_saldo(self, cliente_id: int, nuevo_saldo: float) -> Cliente | None:
        cliente = await self.get_by_id(cliente_id)
        if cliente:
            cliente.saldo = nuevo_saldo
            await self.db.commit()
            await self.db.refresh(cliente)
        return cliente

    async def delete_cliente(self, cliente_id: int) -> bool:
        cliente = await self.get_by_id(cliente_id)
        if cliente:
            await self.delete(cliente)
            return True
        return False

