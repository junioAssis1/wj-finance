from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth import get_current_user_optional

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})

@router.get("/", response_class=HTMLResponse)
def index(request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user, "active_page": "dashboard"}
    )

@router.get("/web/clientes", response_class=HTMLResponse)
def clientes_page(request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="clientes.html",
        context={"user": user, "active_page": "clientes"}
    )

@router.get("/web/clientes/novo", response_class=HTMLResponse)
def novo_cliente_page(request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="novo_cliente.html",
        context={"user": user, "active_page": "clientes", "cliente_id": None}
    )

@router.get("/web/clientes/editar/{id}", response_class=HTMLResponse)
def editar_cliente_page(id: int, request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="novo_cliente.html",
        context={"user": user, "active_page": "clientes", "cliente_id": id}
    )

@router.get("/web/emprestimos", response_class=HTMLResponse)
def emprestimos_page(request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="emprestimos.html",
        context={"user": user, "active_page": "emprestimos"}
    )

@router.get("/web/emprestimos/novo", response_class=HTMLResponse)
def novo_emprestimo_page(request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="novo_emprestimo.html",
        context={"user": user, "active_page": "emprestimos"}
    )

@router.get("/web/emprestimos/{id}/parcelas", response_class=HTMLResponse)
def parcelas_emprestimo_page(id: int, request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="parcelas.html",
        context={"user": user, "active_page": "emprestimos", "emprestimo_id": id}
    )

@router.get("/web/parcelas", response_class=HTMLResponse)
def todas_parcelas_page(request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="todas_parcelas.html",
        context={"user": user, "active_page": "parcelas"}
    )

@router.get("/web/simulador", response_class=HTMLResponse)
def simulador_page(request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="simulador.html",
        context={"user": user, "active_page": "simulador"}
    )

@router.get("/web/relatorios", response_class=HTMLResponse)
def relatorios_page(request: Request, user=Depends(get_current_user_optional)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        request=request,
        name="relatorios.html",
        context={"user": user, "active_page": "relatorios"}
    )
