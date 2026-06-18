from pydantic import BaseModel, Field, ConfigDict

class ProdutoCreate(BaseModel):
    nome: str = Field(..., min_length=1, description="Nome não pode ser vazio")
    preco: float = Field(..., gt=0, description="Preço deve ser maior que zero")
    estoque: int = 0
    ativo: bool = True

class ProdutoResponse(ProdutoCreate):
    id: int
    
    model_config = ConfigDict(from_attributes=True)