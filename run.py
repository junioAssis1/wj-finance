import uvicorn
import os
from seed import seed_database

if __name__ == "__main__":
    print("=" * 60)
    print(" WJ FINANCE - SISTEMA DE GERENCIAMENTO DE EMPRÉSTIMOS ")
    print("=" * 60)
    
    # Executa a semente de dados se necessário
    seed_database()

    print("\nIniciando servidor web...")
    print("Acesse o sistema no seu navegador:")
    print("👉 Interface Web: http://127.0.0.1:8000")
    print("👉 Swagger API Docs: http://127.0.0.1:8000/docs")
    print("👉 ReDoc API: http://127.0.0.1:8000/redoc")
    print("\nCredenciais padrão de acesso:")
    print("E-mail: admin@wjfinance.com")
    print("Senha:  admin123")
    print("=" * 60)

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
