from fastapi import FastAPI
from app.core.database import engine, Base
from app.routers import produtos

# Cria as tabelas (Em um app real, usaríamos o Alembic para isso)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API E-commerce Profissional")

# Registra as rotas que estão em outros arquivos
app.include_router(produtos.router)