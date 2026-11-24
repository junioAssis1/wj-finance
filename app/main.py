import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import (
    auth,
    usuarios,
    clientes,
    emprestimos,
    parcelas,
    pagamentos,
    simulacoes,
    dashboard,
    relatorios,
    web
)

# Criar tabelas no banco de dados automaticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema de Gerenciamento de Empréstimos e Financiamentos com simulação, amortização e dashboard em Python.",
    version="1.0.0"
)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar arquivos estáticos (CSS, JS, Imagens)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Incluir rotas da API REST
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(emprestimos.router)
app.include_router(parcelas.router)
app.include_router(pagamentos.router)
app.include_router(simulacoes.router)
app.include_router(dashboard.router)
app.include_router(relatorios.router)

# Incluir rotas das páginas Web (Jinja2)
app.include_router(web.router)
