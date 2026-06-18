import pytest

# ==============================================================================
# 1. TESTES DE LISTAGEM (GET /produtos)
# ==============================================================================

def test_listar_produtos_banco_vazio(client):
    """[Requisito 4.3.a] Listar produtos quando o banco está vazio"""
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == []

def test_listar_produtos_com_dados(client, produto_existente):
    """[Requisito 4.3.c] Criar produto e verificar que aparece na listagem"""
    response = client.get("/produtos")
    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 1
    assert dados[0]["nome"] == "Produto Cadastrado na Fixture"

# ==============================================================================
# 2. TESTES DE CRIAÇÃO E PERSISTÊNCIA (POST /produtos)
# ==============================================================================

def test_criar_produto_sucesso(client):
    """[Requisito 4.3.b] Criar produto e verificar persistência no banco"""
    payload = {"nome": "Teclado Mecânico", "preco": 350.00, "estoque": 5}
    response = client.post("/produtos", json=payload)
    
    assert response.status_code == 201
    dados = response.json()
    assert "id" in dados
    assert dados["nome"] == payload["nome"]
    
    # Verifica a persistência no banco garantindo que ele aparece na listagem
    get_response = client.get(f"/produtos/{dados['id']}")
    assert get_response.status_code == 200

# ==============================================================================
# 3. TESTES DE VALIDAÇÃO (PARAMETRIZADO)
# ==============================================================================

@pytest.mark.parametrize("payload_invalido", [
    {"preco": 100.0}, # Falta o nome (campo obrigatório)
    {"nome": "Mouse", "preco": -10.0}, # Preço negativo (validação Pydantic: gt=0)
    {"nome": "", "preco": 50.0}, # Nome vazio (validação Pydantic: min_length=1)
])
def test_criar_produto_payload_invalido(client, payload_invalido):
    """[Requisito 4.3.i] Teste parametrizado cobrindo payloads inválidos (status 422)"""
    response = client.post("/produtos", json=payload_invalido)
    assert response.status_code == 422

# ==============================================================================
# 4. TESTES DE BUSCA (GET /produtos/{id})
# ==============================================================================

def test_buscar_produto_sucesso(client, produto_existente):
    """[Requisito 4.3.d] Buscar produto por id — caso de sucesso"""
    produto_id = produto_existente["id"]
    response = client.get(f"/produtos/{produto_id}")
    
    assert response.status_code == 200
    assert response.json()["nome"] == "Produto Cadastrado na Fixture"

def test_buscar_produto_inexistente(client):
    """[Requisito 4.3.e] Buscar produto com id inexistente — deve retornar 404"""
    response = client.get("/produtos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"

# ==============================================================================
# 5. TESTES DE DELEÇÃO (DELETE /produtos/{id})
# ==============================================================================

def test_deletar_produto_sucesso(client, produto_existente):
    """[Requisito 4.3.f] Deletar produto — deve retornar 204"""
    produto_id = produto_existente["id"]
    response = client.delete(f"/produtos/{produto_id}")
    assert response.status_code == 204

def test_deletar_produto_confirmar_remocao(client, produto_existente):
    """[Requisito 4.3.g] Deletar produto e confirmar remoção com GET subsequente"""
    produto_id = produto_existente["id"]
    
    # Deleta
    client.delete(f"/produtos/{produto_id}")
    
    # Tenta buscar novamente
    get_response = client.get(f"/produtos/{produto_id}")
    assert get_response.status_code == 404

def test_deletar_produto_inexistente(client):
    """[Requisito 4.3.h] Deletar produto inexistente — deve retornar 404"""
    response = client.delete("/produtos/999")
    assert response.status_code == 404

# ==============================================================================
# 6. TESTE DE ISOLAMENTO DE ESTADO
# ==============================================================================

def test_verificar_isolamento_de_estado(client):
    """
    [Requisito 4.3.j] Valida que o banco está isolado.
    Como os testes anteriores usaram a fixture 'produto_existente', o banco deve 
    estar vazio novamente no início deste teste por causa do isolamento no conftest.
    """
    response = client.get("/produtos")
    assert response.status_code == 200
    assert response.json() == [] # Garante que nada de testes anteriores sobrou aqui