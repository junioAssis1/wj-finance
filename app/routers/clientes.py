from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Cliente, Usuario
from app.schemas import ClienteCreate, ClienteUpdate, ClienteResponse
from app.auth import get_current_user

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.get("", response_model=List[ClienteResponse])
def listar_clientes(
    q: Optional[str] = Query(None, description="Busca por nome ou CPF"),
    status: Optional[str] = Query(None, description="Filtro por status (Ativo/Inativo)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Cliente)
    if q:
        query = query.filter(
            or_(
                Cliente.nome.ilike(f"%{q}%"),
                Cliente.cpf.ilike(f"%{q}%"),
                Cliente.telefone.ilike(f"%{q}%")
            )
        )
    if status:
        query = query.filter(Cliente.status == status)

    return query.order_by(Cliente.nome.asc()).all()

@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    cliente_in: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Validar CPF único
    existente = db.query(Cliente).filter(Cliente.cpf == cliente_in.cpf.strip()).first()
    if existente:
        raise HTTPException(status_code=400, detail="Já existe um cliente cadastrado com este CPF.")

    novo_cliente = Cliente(
        nome=cliente_in.nome.strip(),
        cpf=cliente_in.cpf.strip(),
        telefone=cliente_in.telefone,
        email=cliente_in.email,
        endereco=cliente_in.endereco,
        dataNascimento=cliente_in.dataNascimento,
        observacoes=cliente_in.observacoes,
        status=cliente_in.status or "Ativo"
    )
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente

@router.get("/{id}", response_model=ClienteResponse)
def obter_cliente(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return cliente

@router.put("/{id}", response_model=ClienteResponse)
def atualizar_cliente(
    id: int,
    dados: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    if dados.cpf is not None and dados.cpf.strip() != cliente.cpf:
        existente = db.query(Cliente).filter(Cliente.cpf == dados.cpf.strip(), Cliente.id != id).first()
        if existente:
            raise HTTPException(status_code=400, detail="Este CPF já pertence a outro cliente.")
        cliente.cpf = dados.cpf.strip()

    if dados.nome is not None:
        cliente.nome = dados.nome.strip()
    if dados.telefone is not None:
        cliente.telefone = dados.telefone
    if dados.email is not None:
        cliente.email = dados.email
    if dados.endereco is not None:
        cliente.endereco = dados.endereco
    if dados.dataNascimento is not None:
        cliente.dataNascimento = dados.dataNascimento
    if dados.observacoes is not None:
        cliente.observacoes = dados.observacoes
    if dados.status is not None:
        cliente.status = dados.status

    db.commit()
    db.refresh(cliente)
    return cliente

@router.delete("/{id}")
def excluir_cliente(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    # Se tiver empréstimos, inativar ou excluir
    if len(cliente.emprestimos) > 0:
        # Permite exclusão em cascata ou inativação
        cliente.status = "Inativo"
        db.commit()
        return {"message": "Cliente possui empréstimos vinculados e foi marcado como Inativo."}

    db.delete(cliente)
    db.commit()
    return {"message": "Cliente excluído com sucesso."}
