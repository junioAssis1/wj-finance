from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    senha = Column(String(255), nullable=False)
    perfil = Column(String(20), default="ADMIN")  # ADMIN, OPERADOR
    ativo = Column(Boolean, default=True)
    createdAt = Column(DateTime, default=datetime.utcnow)

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False, index=True)
    cpf = Column(String(20), unique=True, index=True, nullable=False)
    telefone = Column(String(30), nullable=True)
    email = Column(String(120), nullable=True)
    endereco = Column(String(255), nullable=True)
    dataNascimento = Column(Date, nullable=True)
    observacoes = Column(Text, nullable=True)
    status = Column(String(20), default="Ativo")  # Ativo, Inativo
    createdAt = Column(DateTime, default=datetime.utcnow)

    emprestimos = relationship("Emprestimo", back_populates="cliente", cascade="all, delete-orphan")

class Emprestimo(Base):
    __tablename__ = "emprestimos"

    id = Column(Integer, primary_key=True, index=True)
    clienteId = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    valor = Column(Float, nullable=False)  # Valor principal emprestado
    taxa = Column(Float, nullable=False)  # Ex: 5.0 para 5%
    tipoJuros = Column(String(20), default="compostos")  # simples, compostos
    periodicidade = Column(String(20), default="ao mês")  # ao mês, ao ano
    prazo = Column(Integer, nullable=False)  # Quantidade de parcelas/meses
    data = Column(Date, default=date.today)  # Data da contratação
    primeiroVencimento = Column(Date, nullable=True)
    status = Column(String(30), default="Em aberto")  # Em aberto, Em andamento, Quitado, Atrasado
    totalJuros = Column(Float, default=0.0)
    totalPagar = Column(Float, default=0.0)
    formaPagamento = Column(String(50), nullable=True)  # Pix, Boleto, Dinheiro, Débito
    observacoes = Column(Text, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Cliente", back_populates="emprestimos")
    parcelas = relationship("Parcela", back_populates="emprestimo", cascade="all, delete-orphan", order_by="Parcela.numero")

class Parcela(Base):
    __tablename__ = "parcelas"

    id = Column(Integer, primary_key=True, index=True)
    emprestimoId = Column(Integer, ForeignKey("emprestimos.id"), nullable=False)
    numero = Column(Integer, nullable=False)  # Ex: 1, 2, 3...
    vencimento = Column(Date, nullable=False)
    valorOriginal = Column(Float, nullable=False)  # Valor base da parcela
    juros = Column(Float, default=0.0)             # Parcela de juros
    valorTotal = Column(Float, nullable=False)     # valorOriginal + juros
    valorPago = Column(Float, default=0.0)
    status = Column(String(30), default="Em aberto")  # Em aberto, Pago, Atrasado, Parcial
    dataPagamento = Column(Date, nullable=True)
    diasAtraso = Column(Integer, default=0)
    createdAt = Column(DateTime, default=datetime.utcnow)

    emprestimo = relationship("Emprestimo", back_populates="parcelas")
    pagamentos = relationship("Pagamento", back_populates="parcela", cascade="all, delete-orphan")

class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    parcelaId = Column(Integer, ForeignKey("parcelas.id"), nullable=False)
    valorPago = Column(Float, nullable=False)
    dataPagamento = Column(Date, default=date.today)
    metodoPagamento = Column(String(50), default="Pix")
    observacoes = Column(Text, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow)

    parcela = relationship("Parcela", back_populates="pagamentos")
