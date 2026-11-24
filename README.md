# 💼 WJ Finance - Sistema de Gerenciamento de Empréstimos

> Sistema completo para gestão, controle e simulação de empréstimos e financiamentos, cadastro de clientes, geração de cronograma de parcelas com cálculo financeiro (Price e Juros Simples), controle de atrasos, amortização, pagamentos e dashboard com relatórios gerenciais.

Desenvolvido em **Python** utilizando **FastAPI**, **SQLAlchemy** e **Jinja2**, com interface web responsiva e moderna estilizada conforme o layout de mockup corporativo da **WJ Finance**.

---

## 📸 Visão Geral das Telas e Recursos

O sistema foi estruturado com foco em usabilidade, segurança e integridade de dados financeiros:

1. **🔐 Login Seguro**: Autenticação com e-mail e senha, criptografia com salt individual e tokens JWT (RFC 7519).
2. **📊 Dashboard em Tempo Real**:
   - Total Emprestado
   - Total a Receber
   - Total Recebido
   - Clientes Cadastrados
   - Gráfico de Rosca (*Donut Chart*) com distribuição por status (*Em aberto, Em andamento, Atrasado, Quitado*)
   - Tabela de Próximos Vencimentos com detecção de atraso
3. **👥 Gestão de Clientes**:
   - Cadastro e edição com validação de CPF único, telefone, endereço e dados pessoais
   - Busca instantânea por nome, CPF e telefone
   - Controle de status (`Ativo` / `Inativo`)
   - Histórico de todos os contratos vinculados a cada cliente
4. **💰 Gestão de Empréstimos**:
   - Criação de novos empréstimos com definição de valor principal, taxa de juros, prazo em meses e método de cálculo
   - Prévia financeira calculada em tempo real antes de salvar
   - Geração automática e atômica de todas as parcelas no banco de dados
5. **📅 Controle de Parcelas & Amortização**:
   - Tabela detalhada com amortização, juros e valor total por parcela
   - Identificação automática de parcelas vencidas e contagem de dias de atraso
   - Modal para registro de pagamentos (Pix, Boleto, Dinheiro, Transferência)
   - **Quitação Automática**: quando todas as parcelas são pagas, o status geral do empréstimo passa para `Quitado`
6. **🧮 Simulador de Empréstimo**:
   - Simulação instantânea de valores, taxas e prazos
   - Comparação entre **Juros Compostos (Sistema Price)** e **Juros Simples**
   - Apresentação visual da parcela estimada, montante total e valor de juros
7. **📈 Relatórios & Exportação**:
   - Filtro analítico por intervalo de datas
   - Gráfico de linha de **Evolução de Recebimentos**
   - Exportação de dados para **CSV / Excel** e impressão em PDF

---

## 🛠️ Tecnologias e Arquitetura

- **Linguagem:** Python 3.14
- **Framework Web & API REST:** [FastAPI](https://fastapi.tiangolo.com/) (OpenAPI / Swagger automático)
- **Banco de Dados & ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) com suporte nativo a SQLite e PostgreSQL
- **Validação de Dados:** [Pydantic v2](https://docs.pydantic.dev/)
- **Autenticação:** JWT (*JSON Web Tokens*) com assinatura HMAC-SHA256 e senhas com hash PBKDF2
- **Templates & Interface:** Jinja2, HTML5 semântico, CSS3 Flexbox/Grid e Chart.js
- **Servidor ASGI:** Uvicorn

---

## 📐 Regras de Negócio e Cálculos Financeiros

### 1. Juros Compostos (Sistema Francês / Tabela Price)
O padrão adotado pelo mercado financeiro em parcelamentos calcula prestações constantes ($PMT$) com juros decrescentes sobre o saldo devedor e amortização crescente:

$$PMT = PV \times \frac{i \times (1 + i)^n}{(1 + i)^n - 1}$$

- $PV$: Valor Principal (Montante emprestado)
- $i$: Taxa de juros do período (ex: $5\% = 0{,}05$)
- $n$: Quantidade de parcelas (meses)

### 2. Juros Simples
Utilizado para fins de estudo e contratos simples de prazo fixo:

$$J = PV \times i \times n$$
$$Total = PV + J$$
$$Parcela = \frac{Total}{n}$$

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.10 ou superior instalado

### Passo a passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/junioAssis1/wj-finance.git
   cd wj-finance
   ```

2. **(Opcional) Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   # No Windows:
   .venv\Scripts\activate
   # No Linux/Mac:
   source .venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie a aplicação:**
   ```bash
   python run.py
   ```

O script `run.py` configura automaticamente as tabelas do banco de dados SQLite (`wj_finance.db`) e popula dados iniciais de teste (clientes, empréstimos, parcelas e pagamentos) para você visualizar o dashboard completo logo de início.

---

## 🌐 Acessos e Documentação

- **Aplicação Web:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger UI (Documentação Interativa da API):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 🔑 Credenciais de Acesso Padrão:
- **E-mail:** `admin@wjfinance.com`
- **Senha:** `admin123`
- **Usuário:** `Junio Assis` (ADMIN)

---

## 📁 Estrutura do Projeto

```
wj-finance/
├── app/
│   ├── config.py             # Configurações do sistema e variáveis de ambiente
│   ├── database.py           # Conexão e sessão SQLAlchemy
│   ├── models.py             # Modelos de Dados (Usuario, Cliente, Emprestimo, Parcela, Pagamento)
│   ├── schemas.py            # Validação Pydantic de entrada e saída
│   ├── auth.py               # Autenticação JWT e Hash PBKDF2
│   ├── calculations.py       # Cálculos financeiros (Price, Simples e Atrasos)
│   ├── routers/
│   │   ├── auth.py           # Login e autenticação
│   │   ├── usuarios.py       # CRUD de usuários do sistema
│   │   ├── clientes.py       # CRUD de clientes e histórico
│   │   ├── emprestimos.py    # Empréstimos e parcelamento
│   │   ├── parcelas.py       # Controle de parcelas
│   │   ├── pagamentos.py     # Registro de pagamentos
│   │   ├── simulacoes.py     # Simulador de empréstimos
│   │   ├── dashboard.py      # Indicadores e métricas agregadas
│   │   ├── relatorios.py     # Relatórios e exportação CSV
│   │   └── web.py            # Renderização das páginas HTML
│   ├── static/
│   │   ├── css/style.css     # Estilos da interface WJ Finance
│   │   └── js/app.js         # Lógica de integração e formatação BRL
│   └── templates/            # Telas do sistema (Login, Dashboard, Clientes, etc.)
├── seed.py                   # Script de carga inicial de dados
├── test_app.py               # Testes das regras de negócio
├── run.py                    # Inicializador com Uvicorn
├── requirements.txt          # Dependências do projeto
└── README.md                 # Documentação completa
```

---

## 👤 Autor

Desenvolvido por **Junio Assis**  
GitHub: [@junioAssis1](https://github.com/junioAssis1)
