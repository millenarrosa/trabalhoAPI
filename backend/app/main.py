from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/db_produtos")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    preco = Column(Float)
    quantidade = Column(Integer)

Base.metadata.create_all(bind=engine)

class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    quantidade: int

class ProdutoResponse(ProdutoCreate):
    id: int
    class Config:
        from_attributes = True

app = FastAPI(title="API de Produtos - Backend")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    instancia = os.getenv("INSTANCE_ID", "backend-desconhecido")
    return {"status": "ok", "instancia": instancia}

@app.post("/produtos", response_model=ProdutoResponse)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    db_produto = Produto(nome=produto.nome, preco=produto.preco, quantidade=produto.quantidade)
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto

@app.get("/produtos", response_model=list[ProdutoResponse])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()

    from fastapi import HTTPException # Adicione esta importação lá na primeira linha do arquivo, junto com o FastAPI

@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    # 1. Busca o produto no banco pelo ID
    db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
    
    # 2. Se não existir, devolve erro 404
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # 3. Se existir, deleta e salva a alteração
    db.delete(db_produto)
    db.commit()
    
    return {"status": "ok", "mensagem": "Produto excluído com sucesso"}