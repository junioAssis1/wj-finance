from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# ---- Usuários & Auth ----
class UsuarioBase(BaseModel):
    nome: str
    email: str
    perfil: Optional[str] = "ADMIN"
    ativo: Optional[bool] = True

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    perfil: Optional[str] = None
    ativo: Optional[bool] = None

class UsuarioResponse(UsuarioBase):
    id: int
    createdAt: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse

# ---- Clientes ----
class ClienteBase(BaseModel):
    nome: str
    cpf: str
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    dataNascimento: Optional[date] = None
    observacoes: Optional[str] = None
    status: Optional[str] = "Ativo"

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    dataNascimento: Optional[date] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None

class ClienteResponse(ClienteBase):
    id: int
    createdAt: datetime

    class Config:
        from_attributes = True

# ---- Parcelas ----
class ParcelaResponse(BaseModel):
    id: int
    emprestimoId: int
    numero: int
    vencimento: date
    valorOriginal: float
    juros: float
    valorTotal: float
    valorPago: float
    status: str
    dataPagamento: Optional[date] = None
    diasAtraso: int

    class Config:
        from_attributes = True

class ParcelaUpdate(BaseModel):
    status: Optional[str] = None
    vencimento: Optional[date] = None
    valorTotal: Optional[float] = None

# ---- Empréstimos ----
class EmprestimoCreate(BaseModel):
    clienteId: int
    valor: float = Field(..., gt=0, description="Valor principal")
    taxa: float = Field(..., ge=0, description="Taxa de juros percentual (ex: 5.0)")
    tipoJuros: str = Field("compostos", description="'simples' ou 'compostos'")
    periodicidade: Optional[str] = "ao mês"
    prazo: int = Field(..., gt=0, description="Quantidade de parcelas/meses")
    data: Optional[date] = None
    primeiroVencimento: Optional[date] = None
    formaPagamento: Optional[str] = "Pix"
    observacoes: Optional[str] = None

class EmprestimoResponse(BaseModel):
    id: int
    clienteId: int
    valor: float
    taxa: float
    tipoJuros: str
    periodicidade: str
    prazo: int
    data: date
    primeiroVencimento: Optional[date] = None
    status: str
    totalJuros: float
    totalPagar: float
    formaPagamento: Optional[str] = None
    observacoes: Optional[str] = None
    createdAt: datetime
    cliente: Optional[ClienteResponse] = None
    parcelas: Optional[List[ParcelaResponse]] = []

    class Config:
        from_attributes = True

# ---- Pagamentos ----
class PagamentoCreate(BaseModel):
    parcelaId: int
    valorPago: float = Field(..., gt=0)
    dataPagamento: Optional[date] = None
    metodoPagamento: Optional[str] = "Pix"
    observacoes: Optional[str] = None

class PagamentoResponse(BaseModel):
    id: int
    parcelaId: int
    valorPago: float
    dataPagamento: date
    metodoPagamento: str
    observacoes: Optional[str] = None
    createdAt: datetime

    class Config:
        from_attributes = True

# ---- Simulação ----
class SimulacaoRequest(BaseModel):
    valor: float = Field(..., gt=0)
    taxa: float = Field(..., ge=0)
    prazo: int = Field(..., gt=0)
    tipoJuros: str = "compostos"  # simples ou compostos

class SimulacaoResponse(BaseModel):
    valor_emprestimo: float
    taxa_juros: float
    prazo: int
    tipo_juros: str
    valor_parcela: float
    total_juros: float
    total_pagar: float
    parcelas: List[dict]

# ---- Dashboard ----
class DashboardResponse(BaseModel):
    totalEmprestado: float
    totalReceber: float
    totalRecebido: float
    clientesCadastrados: int
    emprestimosAtivos: int
    totalJurosCalculados: float
    parcelasAtrasadas: int
    statusContagem: dict
    proximosVencimentos: List[dict]
