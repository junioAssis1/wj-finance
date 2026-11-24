from fastapi import APIRouter, HTTPException
from app.schemas import SimulacaoRequest, SimulacaoResponse
from app.calculations import calcular_simulacao

router = APIRouter(prefix="/simulacoes", tags=["Simulações"])

@router.post("", response_model=SimulacaoResponse)
def simular_emprestimo(dados: SimulacaoRequest):
    try:
        resultado = calcular_simulacao(
            valor=dados.valor,
            taxa_percentual=dados.taxa,
            prazo=dados.prazo,
            tipo_juros=dados.tipoJuros
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
