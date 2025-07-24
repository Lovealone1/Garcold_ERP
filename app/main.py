from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session
from app.utils.database.db_connector import get_db
from app.v1_0.repositories import ClienteRepository
from app.v1_0.entities import ClienteDTO

app = FastAPI()

@app.post("/clientes")
async def crear_cliente(cliente_dto: ClienteDTO, db: Session = Depends(get_db)):
    repo = ClienteRepository(db)
    nuevo_cliente = await repo.create_cliente(cliente_dto)
    return nuevo_cliente

@app.get("/clientes/{cliente_id}")
async def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    repo = ClienteRepository(db)
    cliente = await repo.get_by_cc_nit(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.delete("/clientes/{cliente_id}")
async def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    repo = ClienteRepository(db)
    eliminado = await repo.delete_cliente(cliente_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"mensaje": "Cliente eliminado correctamente"}