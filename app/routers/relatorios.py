from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Emprestimo, Parcela, Pagamento, Cliente, Usuario
from app.auth import get_current_user

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

@router.get("")
def obter_relatorio(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Empréstimos no período
    query_emp = db.query(Emprestimo)
    if data_inicio:
        query_emp = query_emp.filter(Emprestimo.data >= data_inicio)
    if data_fim:
        query_emp = query_emp.filter(Emprestimo.data <= data_fim)
    
    emprestimos = query_emp.all()
    emp_ids = [e.id for e in emprestimos]

    total_emprestado = sum(e.valor for e in emprestimos)
    contratos = len(emprestimos)

    # Status contagem
    status_contagem = {"Em aberto": 0, "Em andamento": 0, "Atrasado": 0, "Quitado": 0}
    for e in emprestimos:
        st = e.status
        status_contagem[st] = status_contagem.get(st, 0) + 1

    # Pagamentos no período
    query_pag = db.query(Pagamento)
    if data_inicio:
        query_pag = query_pag.filter(Pagamento.dataPagamento >= data_inicio)
    if data_fim:
        query_pag = query_pag.filter(Pagamento.dataPagamento <= data_fim)
    
    pagamentos = query_pag.all()
    total_recebido = sum(p.valorPago for p in pagamentos)

    # Parcelas vinculadas aos empréstimos
    if emp_ids:
        parcelas = db.query(Parcela).filter(Parcela.emprestimoId.in_(emp_ids)).all()
    else:
        parcelas = []
    
    total_a_receber = sum(max(0.0, p.valorTotal - p.valorPago) for p in parcelas if p.status != "Pago")

    # Evolução temporal dos recebimentos
    evolucao = {}
    for p in pagamentos:
        dia_str = p.dataPagamento.strftime("%d/%m")
        evolucao[dia_str] = evolucao.get(dia_str, 0.0) + p.valorPago

    # Converter em listas ordenadas para gráficos
    labels = list(evolucao.keys())
    valores = [round(evolucao[k], 2) for k in labels]

    return {
        "totalEmprestado": round(total_emprestado, 2),
        "totalReceber": round(total_a_receber, 2),
        "totalRecebido": round(total_recebido, 2),
        "totalContratos": contratos,
        "statusContagem": status_contagem,
        "evolucao": {
            "labels": labels or ["Sem dados"],
            "valores": valores or [0]
        }
    }

@router.get("/exportar-csv")
def exportar_csv(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(Emprestimo).join(Cliente)
    if data_inicio:
        query = query.filter(Emprestimo.data >= data_inicio)
    if data_fim:
        query = query.filter(Emprestimo.data <= data_fim)

    linhas = ["ID;Cliente;CPF;Valor;Taxa;Prazo;Data;Status;Total a Pagar\n"]
    for e in query.all():
        cli_nome = e.cliente.nome if e.cliente else ""
        cli_cpf = e.cliente.cpf if e.cliente else ""
        linhas.append(
            f"{e.id};{cli_nome};{cli_cpf};{e.valor:.2f};{e.taxa}%;{e.prazo};{e.data.strftime('%d/%m/%Y')};{e.status};{e.totalPagar:.2f}\n"
        )

    conteudo = "".join(linhas)
    return Response(
        content=conteudo.encode("utf-8-sig"),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=relatorio_emprestimos.csv"}
    )
