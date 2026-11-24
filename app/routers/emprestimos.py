from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.database import get_db
from app.models import Emprestimo, Parcela, Cliente, Usuario
from app.schemas import EmprestimoCreate, EmprestimoResponse
from app.auth import get_current_user
from app.calculations import calcular_simulacao, add_months, atualizar_status_emprestimo_e_parcelas

router = APIRouter(prefix="/emprestimos", tags=["Empréstimos"])

@router.get("", response_model=List[EmprestimoResponse])
def listar_emprestimos(
    q: Optional[str] = Query(None, description="Busca por nome de cliente"),
    status: Optional[str] = Query(None, description="Filtro de status"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Emprestimo).options(joinedload(Emprestimo.cliente), joinedload(Emprestimo.parcelas))

    if q:
        query = query.join(Cliente).filter(
            or_(
                Cliente.nome.ilike(f"%{q}%"),
                Cliente.cpf.ilike(f"%{q}%")
            )
        )
    if status:
        query = query.filter(Emprestimo.status == status)

    emprestimos = query.order_by(Emprestimo.id.desc()).all()

    # Recalcular status com base na data de hoje
    hoje = date.today()
    alterou = False
    for emp in emprestimos:
        atualizar_status_emprestimo_e_parcelas(emp, hoje)
        alterou = True
    if alterou:
        db.commit()

    return emprestimos

@router.post("", response_model=EmprestimoResponse, status_code=status.HTTP_201_CREATED)
def criar_emprestimo(
    emp_in: EmprestimoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    cliente = db.query(Cliente).filter(Cliente.id == emp_in.clienteId).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    data_emprestimo = emp_in.data or date.today()
    primeiro_vencimento = emp_in.primeiroVencimento or add_months(data_emprestimo, 1)

    # Executar o cálculo financeiro
    calc = calcular_simulacao(
        valor=emp_in.valor,
        taxa_percentual=emp_in.taxa,
        prazo=emp_in.prazo,
        tipo_juros=emp_in.tipoJuros,
        data_inicio=data_emprestimo
    )

    novo_emprestimo = Emprestimo(
        clienteId=emp_in.clienteId,
        valor=emp_in.valor,
        taxa=emp_in.taxa,
        tipoJuros=emp_in.tipoJuros,
        periodicidade=emp_in.periodicidade or "ao mês",
        prazo=emp_in.prazo,
        data=data_emprestimo,
        primeiroVencimento=primeiro_vencimento,
        status="Em aberto",
        totalJuros=calc["total_juros"],
        totalPagar=calc["total_pagar"],
        formaPagamento=emp_in.formaPagamento,
        observacoes=emp_in.observacoes
    )
    db.add(novo_emprestimo)
    db.flush()  # Para obter o ID

    # Gerar as parcelas no banco
    for item in calc["parcelas"]:
        num = item["numero"]
        # Vencimento baseado no primeiroVencimento para a primeira parcela e somas posteriores
        venc = add_months(primeiro_vencimento, num - 1)
        parcela = Parcela(
            emprestimoId=novo_emprestimo.id,
            numero=num,
            vencimento=venc,
            valorOriginal=item["valor_base"],
            juros=item["juros"],
            valorTotal=item["valor_total"],
            valorPago=0.0,
            status="Em aberto"
        )
        db.add(parcela)

    db.commit()
    db.refresh(novo_emprestimo)
    return novo_emprestimo

@router.get("/{id}", response_model=EmprestimoResponse)
def obter_emprestimo(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    emprestimo = db.query(Emprestimo).options(
        joinedload(Emprestimo.cliente),
        joinedload(Emprestimo.parcelas)
    ).filter(Emprestimo.id == id).first()

    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")

    atualizar_status_emprestimo_e_parcelas(emprestimo, date.today())
    db.commit()

    return emprestimo

@router.delete("/{id}")
def excluir_emprestimo(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    emprestimo = db.query(Emprestimo).filter(Emprestimo.id == id).first()
    if not emprestimo:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")

    db.delete(emprestimo)
    db.commit()
    return {"message": "Empréstimo excluído com sucesso."}
