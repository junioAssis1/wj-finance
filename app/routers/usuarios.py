from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.auth import get_current_user, hash_password

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.get("", response_model=List[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return db.query(Usuario).all()

@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    usuario_in: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if db.query(Usuario).filter(Usuario.email == usuario_in.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    novo_usuario = Usuario(
        nome=usuario_in.nome,
        email=usuario_in.email,
        senha=hash_password(usuario_in.senha),
        perfil=usuario_in.perfil or "ADMIN",
        ativo=usuario_in.ativo
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

@router.get("/{id}", response_model=UsuarioResponse)
def obter_usuario(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return usuario

@router.put("/{id}", response_model=UsuarioResponse)
def atualizar_usuario(
    id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if dados.nome is not None:
        usuario.nome = dados.nome
    if dados.email is not None:
        existente = db.query(Usuario).filter(Usuario.email == dados.email, Usuario.id != id).first()
        if existente:
            raise HTTPException(status_code=400, detail="E-mail já está em uso por outro usuário.")
        usuario.email = dados.email
    if dados.senha is not None and dados.senha.strip():
        usuario.senha = hash_password(dados.senha)
    if dados.perfil is not None:
        usuario.perfil = dados.perfil
    if dados.ativo is not None:
        usuario.ativo = dados.ativo

    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/{id}")
def excluir_usuario(
    id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode excluir o seu próprio usuário.")
    
    db.delete(usuario)
    db.commit()
    return {"message": "Usuário removido com sucesso."}
