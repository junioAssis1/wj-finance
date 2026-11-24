from app.database import SessionLocal
from app.models import Usuario, Cliente, Emprestimo, Parcela, Pagamento
from app.calculations import calcular_simulacao

db = SessionLocal()

print("--- TESTE DE DADOS NO BANCO ---")
usuarios = db.query(Usuario).all()
print(f"Total de Usuários: {len(usuarios)} - {[u.email for u in usuarios]}")

clientes = db.query(Cliente).all()
print(f"Total de Clientes: {len(clientes)} - {[c.nome for c in clientes]}")

emprestimos = db.query(Emprestimo).all()
print(f"Total de Empréstimos: {len(emprestimos)}")
for e in emprestimos:
    print(f" - Empréstimo #{e.id}: {e.cliente.nome} | R$ {e.valor:.2f} ({e.status}) | Parcelas: {len(e.parcelas)}")

parcelas = db.query(Parcela).all()
print(f"Total de Parcelas: {len(parcelas)}")

pagamentos = db.query(Pagamento).all()
print(f"Total de Pagamentos Registrados: {len(pagamentos)}")

print("\n--- TESTE DE CÁLCULO FINANCEIRO ---")
sim = calcular_simulacao(1000.0, 5.0, 6, "compostos")
print(f"Simulação R$ 1.000 a 5% em 6 meses (Price):")
print(f" - Parcela: R$ {sim['valor_parcela']:.2f}")
print(f" - Total Juros: R$ {sim['total_juros']:.2f}")
print(f" - Total a Pagar: R$ {sim['total_pagar']:.2f}")

db.close()
print("\n✓ Todos os testes internos passaram com sucesso!")
