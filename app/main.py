from fastapi import FastAPI
from sqlalchemy import text
from app.utils.database.db_connector import engine

app = FastAPI()

@app.get("/clientes")
async def get_clientes():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT * FROM cliente"))
        clientes = [dict(row._mapping) for row in result]
        return {"clientes": clientes}