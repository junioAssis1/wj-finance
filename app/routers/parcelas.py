from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Parcela, Emprestimo, Usuario
from app.schemas import ParcelaResponse, ParcelaUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/parcelas", tags=["Parcelas"])

@router.get("", response_model=List[ParcelaResponse])
def listar_parcelas(
    emprestimo_id: Optional[int] = Query(None, description="Filtrar por empréstimo"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Parcela)
    if emprestimo_id:
        query = query.filter(Parcela.emprestimoId == emprestimo_id)
    if status:
        query = query.filter(Parcela.status == status)

    return query.order_by(Parcela.vencimento.asc()).all()

@router.get("/{id}", response_model=ParcelaResponse)
def obter_parcela(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    parcela = db.query(Parcela).filter(Parcela.id == id).first()
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada.")
    return parcela

@router.put("/{id}", response_model=ParcelaResponse)
def atualizar_parcela(
    id: int,
    dados: ParcelaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    parcela = db.query(Parcela).filter(Parcela.id == id).first()
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada.")

    if dados.status is not None:
        parcela.status = dados.status
    if dados.vencimento is not None:
        parcela.vencimento = dados.vencimento
    if dados.valorTotal is not None:
        parcela.valorTotal = dados.valorTotal

    db.commit()
    db.refresh(parcela)
    return parcela
