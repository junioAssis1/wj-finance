from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models import Usuario, Cliente, Emprestimo, Parcela, Pagamento
from app.auth import hash_password
from app.calculations import calcular_simulacao, add_months, atualizar_status_emprestimo_e_parcelas

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Usuário Administrador
        admin = db.query(Usuario).filter(Usuario.email == "admin@wjfinance.com").first()
        if not admin:
            admin = Usuario(
                nome="Junio Assis",
                email="admin@wjfinance.com",
                senha=hash_password("admin123"),
                perfil="ADMIN",
                ativo=True
            )
            db.add(admin)
            db.commit()
            print("✓ Usuário administrador criado: admin@wjfinance.com / admin123")
        else:
            admin.nome = "Junio Assis"
            db.commit()
            print("✓ Nome do usuário administrador atualizado para: Junio Assis")

        # Verificar se já existem clientes
        if db.query(Cliente).count() > 0:
            print("✓ Banco de dados já possui registros de teste.")
            return

        print("Populando dados de teste fiéis ao mockup...")

        # 2. Clientes
        clientes_dados = [
            {"nome": "João da Silva", "cpf": "123.456.789-00", "telefone": "(62) 99999-0000", "email": "joao@email.com", "endereco": "Av. Brasil, 100", "status": "Ativo"},
            {"nome": "Maria Oliveira", "cpf": "987.654.321-00", "telefone": "(62) 98888-1111", "email": "maria@email.com", "endereco": "Rua das Flores, 45", "status": "Ativo"},
            {"nome": "Carlos Souza", "cpf": "456.789.123-00", "telefone": "(62) 97777-2222", "email": "carlos@email.com", "endereco": "Alameda Central, 789", "status": "Ativo"},
            {"nome": "Ana Paula", "cpf": "321.654.987-00", "telefone": "(62) 96666-3333", "email": "ana@email.com", "endereco": "Rua 15 de Novembro, 12", "status": "Inativo"},
            {"nome": "José Santana", "cpf": "159.753.456-00", "telefone": "(62) 95555-4444", "email": "jose@email.com", "endereco": "Praça da Matriz, 30", "status": "Ativo"},
            {"nome": "Fernanda Lima", "cpf": "753.159.852-00", "telefone": "(62) 94444-5555", "email": "fernanda@email.com", "endereco": "Rua Independência, 204", "status": "Ativo"}
        ]

        clientes_objs = {}
        for c in clientes_dados:
            obj = Cliente(**c)
            db.add(obj)
            clientes_objs[c["nome"]] = obj

        db.commit()

        # 3. Empréstimos e Parcelas
        hoje = date.today()

        # Empréstimo 1: João da Silva - R$ 5.000, 12 parcelas, Em andamento (3 parcelas já pagas)
        data_emp1 = hoje - timedelta(days=95)
        calc1 = calcular_simulacao(5000.0, 5.0, 12, "compostos", data_emp1)
        emp1 = Emprestimo(
            clienteId=clientes_objs["João da Silva"].id,
            valor=5000.0,
            taxa=5.0,
            tipoJuros="compostos",
            periodicidade="ao mês",
            prazo=12,
            data=data_emp1,
            primeiroVencimento=add_months(data_emp1, 1),
            status="Em andamento",
            totalJuros=calc1["total_juros"],
            totalPagar=calc1["total_pagar"],
            formaPagamento="Pix"
        )
        db.add(emp1)
        db.flush()

        for idx, item in enumerate(calc1["parcelas"]):
            venc = add_months(emp1.primeiroVencimento, idx)
            # Pagar as 3 primeiras
            if idx < 3:
                p = Parcela(
                    emprestimoId=emp1.id,
                    numero=item["numero"],
                    vencimento=venc,
                    valorOriginal=item["valor_base"],
                    juros=item["juros"],
                    valorTotal=item["valor_total"],
                    valorPago=item["valor_total"],
                    status="Pago",
                    dataPagamento=venc,
                    diasAtraso=0
                )
                db.add(p)
                db.flush()
                # Registrar pagamento
                db.add(Pagamento(
                    parcelaId=p.id,
                    valorPago=p.valorTotal,
                    dataPagamento=venc,
                    metodoPagamento="Pix"
                ))
            else:
                db.add(Parcela(
                    emprestimoId=emp1.id,
                    numero=item["numero"],
                    vencimento=venc,
                    valorOriginal=item["valor_base"],
                    juros=item["juros"],
                    valorTotal=item["valor_total"],
                    valorPago=0.0,
                    status="Em aberto"
                ))

        # Empréstimo 2: Carlos Souza - R$ 2.500, Atrasado
        data_emp2 = hoje - timedelta(days=60)
        calc2 = calcular_simulacao(2500.0, 5.0, 6, "compostos", data_emp2)
        emp2 = Emprestimo(
            clienteId=clientes_objs["Carlos Souza"].id,
            valor=2500.0,
            taxa=5.0,
            tipoJuros="compostos",
            prazo=6,
            data=data_emp2,
            primeiroVencimento=data_emp2 + timedelta(days=30),
            status="Atrasado",
            totalJuros=calc2["total_juros"],
            totalPagar=calc2["total_pagar"],
            formaPagamento="Boleto"
        )
        db.add(emp2)
        db.flush()
        for idx, item in enumerate(calc2["parcelas"]):
            venc = add_months(emp2.primeiroVencimento, idx)
            status_p = "Atrasado" if venc < hoje else "Em aberto"
            dias = (hoje - venc).days if venc < hoje else 0
            db.add(Parcela(
                emprestimoId=emp2.id,
                numero=item["numero"],
                vencimento=venc,
                valorOriginal=item["valor_base"],
                juros=item["juros"],
                valorTotal=item["valor_total"],
                valorPago=0.0,
                status=status_p,
                diasAtraso=dias
            ))

        # Empréstimo 3: Maria Oliveira - R$ 3.000, Em andamento
        data_emp3 = hoje - timedelta(days=35)
        calc3 = calcular_simulacao(3000.0, 4.5, 6, "compostos", data_emp3)
        emp3 = Emprestimo(
            clienteId=clientes_objs["Maria Oliveira"].id,
            valor=3000.0,
            taxa=4.5,
            tipoJuros="compostos",
            prazo=6,
            data=data_emp3,
            primeiroVencimento=add_months(data_emp3, 1),
            status="Em andamento",
            totalJuros=calc3["total_juros"],
            totalPagar=calc3["total_pagar"],
            formaPagamento="Pix"
        )
        db.add(emp3)
        db.flush()
        for idx, item in enumerate(calc3["parcelas"]):
            venc = add_months(emp3.primeiroVencimento, idx)
            if idx == 0:
                p = Parcela(
                    emprestimoId=emp3.id,
                    numero=item["numero"],
                    vencimento=venc,
                    valorOriginal=item["valor_base"],
                    juros=item["juros"],
                    valorTotal=item["valor_total"],
                    valorPago=item["valor_total"],
                    status="Pago",
                    dataPagamento=venc,
                    diasAtraso=0
                )
                db.add(p)
                db.flush()
                db.add(Pagamento(parcelaId=p.id, valorPago=p.valorTotal, dataPagamento=venc, metodoPagamento="Pix"))
            else:
                db.add(Parcela(
                    emprestimoId=emp3.id,
                    numero=item["numero"],
                    vencimento=venc,
                    valorOriginal=item["valor_base"],
                    juros=item["juros"],
                    valorTotal=item["valor_total"],
                    valorPago=0.0,
                    status="Em aberto"
                ))

        # Empréstimo 4: José Santana - R$ 1.500, Quitado
        data_emp4 = hoje - timedelta(days=120)
        calc4 = calcular_simulacao(1500.0, 3.0, 3, "simples", data_emp4)
        emp4 = Emprestimo(
            clienteId=clientes_objs["José Santana"].id,
            valor=1500.0,
            taxa=3.0,
            tipoJuros="simples",
            prazo=3,
            data=data_emp4,
            primeiroVencimento=add_months(data_emp4, 1),
            status="Quitado",
            totalJuros=calc4["total_juros"],
            totalPagar=calc4["total_pagar"],
            formaPagamento="Pix"
        )
        db.add(emp4)
        db.flush()
        for idx, item in enumerate(calc4["parcelas"]):
            venc = add_months(emp4.primeiroVencimento, idx)
            p = Parcela(
                emprestimoId=emp4.id,
                numero=item["numero"],
                vencimento=venc,
                valorOriginal=item["valor_base"],
                juros=item["juros"],
                valorTotal=item["valor_total"],
                valorPago=item["valor_total"],
                status="Pago",
                dataPagamento=venc,
                diasAtraso=0
            )
            db.add(p)
            db.flush()
            db.add(Pagamento(parcelaId=p.id, valorPago=p.valorTotal, dataPagamento=venc, metodoPagamento="Pix"))

        # Atualizar status gerais
        for emp in [emp1, emp2, emp3, emp4]:
            atualizar_status_emprestimo_e_parcelas(emp, hoje)

        db.commit()
        print("✓ Banco de dados populado com sucesso com dados de simulação e clientes!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
