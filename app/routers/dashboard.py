from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.models import Cliente, Emprestimo, Parcela, Usuario
from app.schemas import DashboardResponse
from app.auth import get_current_user
from app.calculations import atualizar_status_emprestimo_e_parcelas

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardResponse)
def obter_dashboard(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    hoje = date.today()

    # Recalcular status de empréstimos
    emprestimos = db.query(Emprestimo).options(joinedload(Emprestimo.parcelas)).all()
    for emp in emprestimos:
        atualizar_status_emprestimo_e_parcelas(emp, hoje)
    db.commit()

    # Total emprestado
    total_emprestado = db.query(func.coalesce(func.sum(Emprestimo.valor), 0.0)).scalar()

    # Parcelas
    parcelas = db.query(Parcela).all()
    total_recebido = sum(p.valorPago for p in parcelas)
    total_a_receber = sum(max(0.0, p.valorTotal - p.valorPago) for p in parcelas if p.status != "Pago")
    parcelas_atrasadas = sum(1 for p in parcelas if p.status == "Atrasado")

    # Clientes cadastrados
    clientes_cadastrados = db.query(Cliente).filter(Cliente.status == "Ativo").count()

    # Status de empréstimos
    status_contagem = {
        "Em aberto": 0,
        "Em andamento": 0,
        "Atrasado": 0,
        "Quitado": 0
    }
    emprestimos_ativos = 0
    total_juros = 0.0

    for emp in emprestimos:
        st = emp.status
        if st in status_contagem:
            status_contagem[st] += 1
        else:
            status_contagem[st] = 1

        if st in ["Em aberto", "Em andamento", "Atrasado"]:
            emprestimos_ativos += 1

        total_juros += (emp.totalJuros or 0.0)

    # Próximos Vencimentos (Parcelas em aberto ou atrasadas ordenadas por vencimento)
    proximas_parcelas = db.query(Parcela).options(
        joinedload(Parcela.emprestimo).joinedload(Emprestimo.cliente)
    ).filter(
        Parcela.status.in_(["Em aberto", "Atrasado"])
    ).order_by(Parcela.vencimento.asc()).limit(6).all()

    proximos_vencimentos = []
    for p in proximas_parcelas:
        cliente_nome = p.emprestimo.cliente.nome if p.emprestimo and p.emprestimo.cliente else "Desconhecido"
        proximos_vencimentos.append({
            "parcela_id": p.id,
            "cliente_nome": cliente_nome,
            "valor": p.valorTotal,
            "vencimento": p.vencimento.strftime("%d/%m/%Y"),
            "status": p.status,
            "dias_atraso": p.diasAtraso
        })

    return {
        "totalEmprestado": round(total_emprestado, 2),
        "totalReceber": round(total_a_receber, 2),
        "totalRecebido": round(total_recebido, 2),
        "clientesCadastrados": clientes_cadastrados,
        "emprestimosAtivos": emprestimos_ativos,
        "totalJurosCalculados": round(total_juros, 2),
        "parcelasAtrasadas": parcelas_atrasadas,
        "statusContagem": status_contagem,
        "proximosVencimentos": proximos_vencimentos
    }
