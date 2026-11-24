import calendar
from datetime import date, timedelta
from typing import List, Dict, Any

def add_months(start_date: date, months: int) -> date:
    """Adiciona 'months' meses a uma data considerando fins de mês."""
    new_month = start_date.month - 1 + months
    new_year = start_date.year + new_month // 12
    new_month = new_month % 12 + 1
    # Tratar dias do mês que não existem no mês alvo (ex: 31 de fev)
    import calendar
    max_days = calendar.monthrange(new_year, new_month)[1]
    day = min(start_date.day, max_days)
    return date(new_year, new_month, day)

def calcular_simulacao(
    valor: float,
    taxa_percentual: float,
    prazo: int,
    tipo_juros: str = "compostos",
    data_inicio: date = None
) -> Dict[str, Any]:
    """
    Calcula os valores do empréstimo e a lista de parcelas.
    taxa_percentual: Ex: 5.0 para 5% ao mês.
    prazo: Número de meses/parcelas.
    tipo_juros: 'simples' ou 'compostos' (Sistema Price)
    """
    if valor <= 0 or prazo <= 0:
        raise ValueError("Valor e prazo devem ser maiores que zero.")

    if data_inicio is None:
        data_inicio = date.today()

    i = taxa_percentual / 100.0
    parcelas: List[Dict[str, Any]] = []

    if tipo_juros.lower() == "simples":
        # Juros Simples: J = C * i * n
        total_juros = valor * i * prazo
        total_pagar = valor + total_juros
        valor_parcela = total_pagar / prazo
        juros_por_parcela = total_juros / prazo
        base_por_parcela = valor / prazo

        for n in range(1, prazo + 1):
            venc = add_months(data_inicio, n)
            parcelas.append({
                "numero": n,
                "vencimento": venc.isoformat(),
                "valor_base": round(base_por_parcela, 2),
                "juros": round(juros_por_parcela, 2),
                "valor_total": round(valor_parcela, 2)
            })
    else:
        # Juros Compostos (Sistema Price)
        if i == 0:
            valor_parcela = valor / prazo
            total_pagar = valor
            total_juros = 0.0
            for n in range(1, prazo + 1):
                venc = add_months(data_inicio, n)
                parcelas.append({
                    "numero": n,
                    "vencimento": venc.isoformat(),
                    "valor_base": round(valor_parcela, 2),
                    "juros": 0.0,
                    "valor_total": round(valor_parcela, 2)
                })
        else:
            # PMT = PV * (i * (1 + i)^n) / ((1 + i)^n - 1)
            fator = (1 + i) ** prazo
            valor_parcela = valor * (i * fator) / (fator - 1)
            total_pagar = valor_parcela * prazo
            total_juros = total_pagar - valor

            saldo_devedor = valor
            for n in range(1, prazo + 1):
                venc = add_months(data_inicio, n)
                juros_parcela = saldo_devedor * i
                amortizacao = valor_parcela - juros_parcela
                saldo_devedor = max(0.0, saldo_devedor - amortizacao)

                parcelas.append({
                    "numero": n,
                    "vencimento": venc.isoformat(),
                    "valor_base": round(amortizacao, 2),
                    "juros": round(juros_parcela, 2),
                    "valor_total": round(valor_parcela, 2)
                })

    return {
        "valor_emprestimo": round(valor, 2),
        "taxa_juros": round(taxa_percentual, 2),
        "prazo": prazo,
        "tipo_juros": tipo_juros,
        "valor_parcela": round(valor_parcela, 2),
        "total_juros": round(total_juros, 2),
        "total_pagar": round(total_pagar, 2),
        "parcelas": parcelas
    }

def atualizar_status_emprestimo_e_parcelas(emprestimo, hoje: date = None):
    """
    Atualiza os status das parcelas e do empréstimo de acordo com as datas e pagamentos.
    """
    if hoje is None:
        hoje = date.today()

    todas_pagas = True
    tem_atrasada = False
    tem_paga = False

    for p in emprestimo.parcelas:
        if p.status == "Pago":
            tem_paga = True
            p.diasAtraso = 0
            continue

        todas_pagas = False
        if p.vencimento < hoje:
            dias = (hoje - p.vencimento).days
            p.diasAtraso = dias
            p.status = "Atrasado"
            tem_atrasada = True
        else:
            p.diasAtraso = 0
            p.status = "Em aberto"

    if todas_pagas and len(emprestimo.parcelas) > 0:
        emprestimo.status = "Quitado"
    elif tem_atrasada:
        emprestimo.status = "Atrasado"
    elif tem_paga:
        emprestimo.status = "Em andamento"
    else:
        emprestimo.status = "Em aberto"
