import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ==============================================================================
# CONFIGURAÇÃO DO AMBIENTE DE TESTES
# ==============================================================================
# Forçamos a variável de ambiente ANTES de importar o 'main.py'.
# Assim, quando o 'main' for carregado, o SQLAlchemy usará o banco de testes (porta 5435).
TEST_DATABASE_URL = "postgresql+psycopg2://admin:adminpassword@localhost:5435/ecommerce_test"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.main import app
from app.core.database import Base, get_db
# Cria um engine e uma sessão exclusivos para rodar dentro dos testes
engine_test = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

# ==============================================================================
# FIXTURES OBRIGATÓRIAS
# ==============================================================================

@pytest.fixture(scope="function")
def client():
    """
    Fixture principal que garante o isolamento total entre os testes.
    A cada função de teste executada, o banco é resetado do zero.
    """
    # (a) Cria todas as tabelas limpas no banco de testes antes do teste rodar
    Base.metadata.create_all(bind=engine_test)
    
    # (b) Configura o dependency_overrides para substituir o get_db da API original
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    # (c) Faz o yield do TestClient para ser usado nas funções de teste
    with TestClient(app) as c:
        yield c
        
    # (d) TEARDOWN: Limpa os overrides e destrói tudo após a execução do teste
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def produto_existente(client):
    """
    Fixture auxiliar que depende de 'client' e já deixa um produto cadastrado
    no banco de dados para testes de busca, deleção ou listagem.
    """
    payload = {
        "nome": "Produto Cadastrado na Fixture",
        "preco": 49.90,
        "estoque": 10,
        "ativo": True
    }
    # Cria o produto usando o próprio client para persistir no banco de testes temporário
    response = client.post("/produtos", json=payload)
    return response.json()