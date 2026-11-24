# WJ Finance - Sistema de Gerenciamento de Empréstimos (Python)

Sistema completo de gerenciamento de clientes, empréstimos, parcelamento, controle de atrasos, amortização, simulação financeira e dashboard analítico, desenvolvido em **Python** com **FastAPI** e **SQLAlchemy**, baseado na especificação do projeto e no layout do mockup **WJ Finance**.

---

## 🚀 Tecnologias Utilizadas

- **Linguagem:** Python 3
- **Framework Web & API:** FastAPI
- **Banco de Dados & ORM:** SQLite / PostgreSQL via SQLAlchemy
- **Modelagem & Validação:** Pydantic v2
- **Segurança & Autenticação:** JWT (JSON Web Tokens) com HS256 e PBKDF2-SHA256 para senhas
- **Frontend & Templates:** Jinja2, HTML5 moderno, CSS3 responsivo e Chart.js
- **Servidor ASGI:** Uvicorn

---

## 🎯 Módulos Implementados

1. **Módulo de Autenticação & Usuários:**
   - Cadastro, listagem e gerenciamento de usuários do sistema.
   - Login com e-mail e senha com hash PBKDF2 e geração de Token JWT.
   - Suporte a perfis de acesso (`ADMIN`, `OPERADOR`).
   - Autenticação transparente tanto via Header `Authorization: Bearer <token>` quanto via Cookie seguro para o navegador.

2. **Módulo de Clientes:**
   - CRUD completo de clientes (Nome, CPF único, Telefone, E-mail, Endereço, Data de Nascimento, Observações).
   - Filtros de busca por nome e CPF em tempo real.
   - Controle de status (`Ativo`, `Inativo`).
   - Relacionamento 1:N com histórico de empréstimos.

3. **Módulo de Empréstimos:**
   - Registro de valor principal, taxa de juros (mensal/anual), prazo em meses e método de cálculo (Juros Compostos / Sistema Francês Price ou Juros Simples).
   - Cálculo automático e geração instantânea de todo o cronograma de parcelas.
   - Controle de status automatizado: `Em aberto`, `Em andamento`, `Quitado`, `Atrasado`.

4. **Módulo de Parcelas e Pagamentos:**
   - Cronograma detalhado com número da parcela, vencimento, amortização, juros e valor total.
   - Modal interativo para registrar pagamentos (Pix, Boleto, Dinheiro, Transferência).
   - Atualização automática de dias de atraso conforme a data atual.
   - Quitação automática do empréstimo quando todas as parcelas forem pagas.

5. **Simulador de Empréstimo:**
   - Permite simular valores, taxas e prazos antes da contratação.
   - Cálculo comparativo entre Juros Simples e Compostos (Price).
   - Apresentação visual de valor da parcela, total de juros e montante total a pagar.

6. **Dashboard Analítico:**
   - Cards com indicadores em tempo real:
     - **Total Emprestado**
     - **Total a Receber**
     - **Total Recebido**
     - **Clientes Cadastrados**
   - Gráfico em Rosca (Donut Chart) com distribuição de Empréstimos por Status.
   - Tabela de Próximos Vencimentos com alertas de parcelas em atraso.

7. **Relatórios Financeiros:**
   - Filtros por intervalo de datas.
   - Gráfico de linha de Evolução de Recebimentos.
   - Exportação de dados para **CSV / Excel** com um clique e impressão em PDF.

---

## 📦 Como Executar o Projeto

### 1. Iniciar o Sistema
Basta executar o script `run.py`:

```bash
python run.py
```

O script inicializa automaticamente as tabelas do banco de dados SQLite (`wj_finance.db`) e popula os dados iniciais de teste (clientes, empréstimos e parcelas) se o banco for novo.

### 2. Acessar a Aplicação
Abra seu navegador e acesse:

- **Interface Visual do Sistema:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentação Interativa Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentação ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 3. Credenciais Padrão de Acesso
- **E-mail:** `admin@wjfinance.com`
- **Senha:** `admin123`

---

## 📁 Estrutura de Arquivos

```
Projeto investimento/
├── app/
│   ├── __init__.py
│   ├── config.py             # Configurações do sistema e variáveis de ambiente
│   ├── database.py           # Conexão e Sessão SQLAlchemy
│   ├── models.py             # Modelos de Dados (Usuario, Cliente, Emprestimo, Parcela, Pagamento)
│   ├── schemas.py            # Schemas Pydantic para validação
│   ├── auth.py               # Autenticação JWT e Hash de Senhas
│   ├── calculations.py       # Cálculos financeiros (Price, Juros Simples, Atrasos)
│   ├── routers/
│   │   ├── auth.py           # Endpoints de Login e Logout
│   │   ├── usuarios.py       # CRUD de Usuários
│   │   ├── clientes.py       # CRUD de Clientes
│   │   ├── emprestimos.py    # Gestão de Empréstimos
│   │   ├── parcelas.py       # Gestão de Parcelas
│   │   ├── pagamentos.py     # Registro de Pagamentos
│   │   ├── simulacoes.py     # Simulador de Empréstimos
│   │   ├── dashboard.py      # Métricas e Indicadores
│   │   ├── relatorios.py     # Relatórios e Exportação CSV
│   │   └── web.py            # Rotas para renderização das páginas HTML
│   ├── static/
│   │   ├── css/style.css     # Estilização visual fiel ao mockup
│   │   └── js/app.js         # Utilitários e integração com a API
│   └── templates/
│       ├── base.html         # Sidebar, Topbar e estrutura comum
│       ├── login.html        # Tela de Login (Split banner)
│       ├── dashboard.html    # Tela de Dashboard com Cards e Gráficos
│       ├── clientes.html     # Listagem de Clientes
│       ├── novo_cliente.html # Formulário de Cadastro/Edição de Cliente
│       ├── emprestimos.html  # Listagem de Empréstimos
│       ├── novo_emprestimo.html # Cadastro de Empréstimo com prévia em tempo real
│       ├── parcelas.html     # Cronograma de Parcelas e Modal de Pagamento
│       ├── todas_parcelas.html # Visão geral de parcelas e atrasos
│       ├── simulador.html    # Simulador interativo com cálculo imediato
│       └── relatorios.html   # Relatórios com filtros e exportação
├── seed.py                   # Script de carga inicial de dados realistas
├── test_app.py               # Testes de integração das regras de negócio
├── run.py                    # Script de inicialização do servidor
├── requirements.txt          # Dependências do projeto
└── README.md                 # Documentação completa
```
