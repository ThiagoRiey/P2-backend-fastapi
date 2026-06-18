# Atividade Avaliativa — API de Catálogo de E-commerce
## Testes Automatizados com Pytest, FastAPI e PostgreSQL via Docker

Este projeto consiste numa API REST modular desenvolvida com **FastAPI**, **SQLAlchemy ORM** e **Pydantic**, totalmente integrada com uma suíte de testes automatizados utilizando **Pytest** que roda contra um banco de dados real **PostgreSQL** provisionado via **Docker**.

A arquitetura segue as melhores práticas de mercado, organizando o projeto de forma modular e profissional com a separação clara de responsabilidades.

---

## Estrutura do Repositório
```
seu_repositorio/
├── app/
│   ├── core/
│   │   └── database.py     # Configuração e conexão do SQLAlchemy + get_db
│   ├── models/
│   │   └── produto.py      # Modelo ORM do banco de dados (tabela produtos)
│   ├── routers/
│   │   └── produtos.py     # Endpoints da API (CRUD de produtos com APIRouter)
│   ├── schemas/
│   │   └── produto.py      # Schemas de validação e serialização do Pydantic
│   └── main.py             # Inicialização do FastAPI e inclusão dos roteadores
├── tests/
│   ├── __init__.py
│   └── test_produtos.py    # Suíte de testes automatizados (mínimo de 10 cenários)
├── conftest.py             # Configuração do Pytest, overrides e fixtures de isolamento
├── docker-compose.yml      # Orquestração dos serviços PostgreSQL (Dev e Testes)
├── requirements.txt        # Dependências do projeto Python
└── README.md               # Documentação oficial do projeto
```
---

# 1. Como Subir o Banco de Testes com Docker
O projeto utiliza dois serviços independentes de PostgreSQL no Docker Compose para garantir que o ambiente de desenvolvimento local e o de testes automatizados não sofram interferências mútuas.

Para inicializar ambos os contêineres, execute o seguinte comando na raiz do projeto:

docker-compose up -d

Detalhes da Infraestrutura Configurada:
Banco de Desenvolvimento (db_dev): Acessível localmente na porta 5434, mapeado com volumes persistentes para manter os dados salvos.

Banco de Testes (db_test): Acessível localmente na porta 5435, sem volumes persistentes. Sendo totalmente efêmero, os dados de teste são descartáveis e destruídos.

---
# 2. Como Executar a Aplicação Localmente
Após garantir que os contêineres do Docker estão saudáveis, ative o seu ambiente virtual (venv) e execute o servidor Uvicorn:

uvicorn app.main:app --reload

A documentação interativa da API ficará acessível no navegador através do endereço:

 http://localhost:8000/docs

---

# 3. Comando Exato para Executar os Testes
Para rodar a suíte completa com as validações de cobertura de código exigidas, ative o ambiente virtual e execute o seguinte comando no terminal:

pytest --cov=app -v

# 4. Saída Esperada do Pytest
Ao executar o comando acima, a suíte processará as funções de teste, gerando o relatório detalhado de cobertura da pasta app/. A saída esperada do console retorna 12 testes passados com sucesso e 94% de cobertura total:

tests/test_produtos.py::test_listar_produtos_banco_vazio PASSED
tests/test_produtos.py::test_listar_produtos_com_dados PASSED
tests/test_produtos.py::test_criar_produto_sucesso PASSED
tests/test_produtos.py::test_criar_produto_payload_invalido[payload_invalido0] PASSED
tests/test_produtos.py::test_criar_produto_payload_invalido[payload_invalido1] PASSED
tests/test_produtos.py::test_criar_produto_payload_invalido[payload_invalido2] PASSED
tests/test_produtos.py::test_buscar_produto_sucesso PASSED
tests/test_produtos.py::test_buscar_produto_inexistente PASSED
tests/test_produtos.py::test_deletar_produto_sucesso PASSED
tests/test_produtos.py::test_deletar_produto_confirmar_remocao PASSED
tests/test_produtos.py::test_deletar_produto_inexistente PASSED
tests/test_produtos.py::test_verificar_isolamento_de_estado PASSED

-------------------------------------- coverage --------------------------------------
Name                     Stmts   Miss  Cover
--------------------------------------------
app\core\database.py       12      4    67%
app\main.py                 6      0   100%
app\models\produto.py       9      0   100%
app\routers\produtos.py    30      0   100%
app\schemas\produto.py      8      0   100%
--------------------------------------------
TOTAL                       65      4    94%

---
# 5. Explicação do Isolamento entre Testes
## O isolamento total do estado da base de dados entre as execuções dos testes foi implementado no arquivo conftest.py através do uso correto de yield e fixtures do Pytest:

1 Setup (Criação): Antes de cada função de teste ser executada (scope="function"), a fixture principal utiliza o Base.metadata.create_all(bind=engine_test) para criar todas as tabelas limpas e vazias no banco de testes (porta 5435).

2 Dependency Overrides: Para garantir que a API use o banco de testes em vez do banco de desenvolvimento, utilizamos o app.dependency_overrides para substituir a função original get_db por uma nova sessão conectada exclusivamente ao db_test.

3 Execução Isolada: O controle é passado para o teste através do yield, entregando um TestClient configurado.

4 Teardown (Destruição): Imediatamente após a conclusão do teste (seja com sucesso ou falha), a limpeza é acionada. O override é limpo (clear()) e todas as tabelas são destruídas utilizando o Base.metadata.drop_all(bind=engine_test), garantindo que nenhum resíduo de dados afete o teste seguinte.
