from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pagamento, Parcela, Emprestimo, Usuario
from app.schemas import PagamentoCreate, PagamentoResponse
from app.auth import get_current_user
from app.calculations import atualizar_status_emprestimo_e_parcelas

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

@router.get("", response_model=List[PagamentoResponse])
def listar_pagamentos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return db.query(Pagamento).order_by(Pagamento.id.desc()).all()

@router.post("", response_model=PagamentoResponse, status_code=status.HTTP_201_CREATED)
def registrar_pagamento(
    pag_in: PagamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    parcela = db.query(Parcela).filter(Parcela.id == pag_in.parcelaId).first()
    if not parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada.")

    data_pag = pag_in.dataPagamento or date.today()

    novo_pagamento = Pagamento(
        parcelaId=pag_in.parcelaId,
        valorPago=pag_in.valorPago,
        dataPagamento=data_pag,
        metodoPagamento=pag_in.metodoPagamento or "Pix",
        observacoes=pag_in.observacoes
    )
    db.add(novo_pagamento)

    # Atualizar parcela
    parcela.valorPago += pag_in.valorPago
    if parcela.valorPago >= (parcela.valorTotal - 0.01):  # Tolerância de arredondamento
        parcela.status = "Pago"
        parcela.dataPagamento = data_pag
        parcela.diasAtraso = 0
    else:
        parcela.status = "Parcial"

    # Atualizar status do empréstimo
    emprestimo = db.query(Emprestimo).filter(Emprestimo.id == parcela.emprestimoId).first()
    if emprestimo:
        atualizar_status_emprestimo_e_parcelas(emprestimo, date.today())

    db.commit()
    db.refresh(novo_pagamento)
    return novo_pagamento
