import streamlit as st
from datetime import datetime, date

st.set_page_config(page_title="Painel para Advogados", layout="wide")

# Inicializa estados
if 'clients' not in st.session_state:
    st.session_state.clients = []
if 'cases' not in st.session_state:
    st.session_state.cases = []
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'events' not in st.session_state:
    st.session_state.events = []
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'documents' not in st.session_state:
    st.session_state.documents = []

if 'show_add_client' not in st.session_state:
    st.session_state.show_add_client = False
if 'show_add_case' not in st.session_state:
    st.session_state.show_add_case = False
if 'show_add_task' not in st.session_state:
    st.session_state.show_add_task = False
if 'show_add_event' not in st.session_state:
    st.session_state.show_add_event = False
if 'show_add_transaction' not in st.session_state:
    st.session_state.show_add_transaction = False
if 'show_add_document' not in st.session_state:
    st.session_state.show_add_document = False
if 'show_add_income' not in st.session_state:
    st.session_state.show_add_income = False
if 'show_add_expense' not in st.session_state:
    st.session_state.show_add_expense = False

menu = st.sidebar.selectbox(
    "Menu",[
        "Visão Geral",
        "Clientes",
        "Casos",
        "Documentos",
        "Agenda",
        "Tarefas",
        "Casos por Cliente",
        "Financeiro"
    ]
)

# Funções auxiliares

def add_client(name, email, phone, notes):
    st.session_state.clients.append({
        "Nome": name,
        "Email": email,
        "Telefone": phone,
        "Anotações": notes,
    })

def add_case(client, process_number, parties, lawyer, start_date, status):
    st.session_state.cases.append({
        "Cliente": client,
        "Processo": process_number,
        "Partes": parties,
        "Advogado": lawyer,
        "Data de Abertura": start_date,
        "Status": status,
    })

def add_task(description, priority, due_date, client, related_case):
    st.session_state.tasks.append({
        "Descrição": description,
        "Prioridade": priority,
        "Prazo": due_date,
        "Cliente": client,
        "Caso": related_case,
    })

def add_event(title, event_type, event_datetime, location, client, case, status, description):
    st.session_state.events.append({
        "Título": title,
        "Tipo": event_type,
        "Data": event_datetime,
        "Local": location,
        "Cliente": client,
        "Caso": case,
        "Status": status,
        "Descrição": description,
    })

def add_transaction(kind, category, amount, description, trans_date, payment_status, client, case):
    st.session_state.transactions.append({
        "Tipo": kind,
        "Categoria": category,
        "Valor": amount,
        "Descrição": description,
        "Data": trans_date,
        "Status": payment_status,
        "Cliente": client,
        "Caso": case,
    })

def add_document(client, case, title, file):
    st.session_state.documents.append({
        "Cliente": client,
        "Caso": case,
        "Título": title,
        "Arquivo": file.name if file else "",
    })

# Páginas
if menu == "Visão Geral":
    st.title("Painel Geral")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clientes", len(st.session_state.clients))
    col2.metric("Casos", len(st.session_state.cases))
    col3.metric("Tarefas", len(st.session_state.tasks))
    saldo = sum(t['Valor'] if t['Tipo'] == 'Entrada' else -t['Valor'] for t in st.session_state.transactions)
    col4.metric("Saldo", f"R$ {saldo:,.2f}")
    st.subheader("Próximos eventos")
    if st.session_state.events:
        st.table(st.session_state.events)
    else:
        st.info("Nenhum evento cadastrado")

elif menu == "Clientes":
    st.title("Clientes")
    if st.button("Adicionar Cliente"):
        st.session_state.show_add_client = not st.session_state.show_add_client
    if st.session_state.show_add_client:
        with st.expander("Adicionar Cliente", expanded=True):
            with st.form("add_client"):
                name = st.text_input("Nome Completo *")
                email = st.text_input("E-mail")
                phone = st.text_input("Telefone")
                notes = st.text_area("Anotações / Preferências")
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    add_client(name, email, phone, notes)
                    st.success("Cliente adicionado")
    st.subheader("Lista de Clientes")
    if st.session_state.clients:
        st.table(st.session_state.clients)
    else:
        st.info("Nenhum cliente cadastrado")

elif menu == "Casos":
    st.title("Casos")
    if st.button("Adicionar Caso"):
        st.session_state.show_add_case = not st.session_state.show_add_case
    if st.session_state.show_add_case:
        with st.expander("Adicionar Caso", expanded=True):
            with st.form("add_case"):
                client = st.selectbox(
                    "Cliente *",
                    [c['Nome'] for c in st.session_state.clients]
                ) if st.session_state.clients else st.text_input("Cliente *")
                process_number = st.text_input("Nº do Processo *")
                parties = st.text_area("Partes Envolvidas")
                lawyer = st.text_input("Advogado Responsável")
                start_date = st.date_input("Data de Abertura", value=date.today())
                status = st.selectbox("Status", ["Ativo", "Encerrado", "Suspenso"])
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    add_case(client, process_number, parties, lawyer, start_date, status)
                    st.success("Caso adicionado")
    st.subheader("Lista de Casos")
    if st.session_state.cases:
        st.table(st.session_state.cases)
    else:
        st.info("Nenhum caso cadastrado")

elif menu == "Documentos":
    st.title("Documentos")
    if st.button("Anexar Documento"):
        st.session_state.show_add_document = not st.session_state.show_add_document
    if st.session_state.show_add_document:
        with st.expander("Anexar Documento", expanded=True):
            with st.form("add_document"):
                client = st.selectbox(
                    "Cliente *",
                    [c['Nome'] for c in st.session_state.clients]
                ) if st.session_state.clients else st.text_input("Cliente *")
                case = st.selectbox(
                    "Vincular ao Caso (opcional)",
                    ["Nenhum"] + [c['Processo'] for c in st.session_state.cases]
                )
                title = st.text_input("Título / Descrição *")
                file = st.file_uploader("Arquivo *")
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    case_val = None if case == "Nenhum" else case
                    add_document(client, case_val, title, file)
                    st.success("Documento anexado")
    st.subheader("Documentos")
    if st.session_state.documents:
        st.table([{k: v for k, v in d.items() if k != "Arquivo"} for d in st.session_state.documents])
    else:
        st.info("Nenhum documento anexado")

elif menu == "Agenda":
    st.title("Agenda")
    if st.button("Adicionar Evento"):
        st.session_state.show_add_event = not st.session_state.show_add_event
    if st.session_state.show_add_event:
        with st.expander("Adicionar Evento", expanded=True):
            with st.form("add_event"):
                title = st.text_input("Título *")
                event_type = st.selectbox("Tipo de Evento *", ["Audiência", "Prazo", "Reunião"])
                event_day = st.date_input("Data *", value=date.today())
                event_time = st.time_input("Hora *", value=datetime.now().time())
                location = st.text_input("Local / Link")
                client = st.selectbox(
                    "Vincular ao Cliente",
                    ["Nenhum"] + [c['Nome'] for c in st.session_state.clients]
                )
                case = st.selectbox(
                    "Vincular ao Caso",
                    ["Nenhum"] + [c['Processo'] for c in st.session_state.cases]
                )
                status = st.selectbox("Status", ["Agendado", "Concluído", "Cancelado"])
                description = st.text_area("Descrição")
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    client_val = None if client == "Nenhum" else client
                    case_val = None if case == "Nenhum" else case
                    dt = datetime.combine(event_day, event_time)
                    add_event(title, event_type, dt, location, client_val, case_val, status, description)
                    st.success("Evento adicionado")
    st.subheader("Eventos")
    if st.session_state.events:
        st.table(st.session_state.events)
    else:
        st.info("Nenhum evento cadastrado")

elif menu == "Tarefas":
    st.title("Tarefas")
    if st.button("Adicionar Tarefa"):
        st.session_state.show_add_task = not st.session_state.show_add_task
    if st.session_state.show_add_task:
        with st.expander("Adicionar Tarefa", expanded=True):
            with st.form("add_task"):
                description = st.text_input("Descrição *")
                priority = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
                due_date = st.date_input("Data do Prazo", value=date.today())
                client = st.selectbox(
                    "Vincular ao Cliente",
                    ["Nenhum"] + [c['Nome'] for c in st.session_state.clients]
                )
                related_case = st.selectbox(
                    "Vincular ao Caso",
                    ["Nenhum"] + [c['Processo'] for c in st.session_state.cases]
                )
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    client_val = None if client == "Nenhum" else client
                    case_val = None if related_case == "Nenhum" else related_case
                    add_task(description, priority, due_date, client_val, case_val)
                    st.success("Tarefa adicionada")
    st.subheader("Lista de Tarefas")
    if st.session_state.tasks:
        st.table(st.session_state.tasks)
    else:
        st.info("Nenhuma tarefa cadastrada")

elif menu == "Casos por Cliente":
    st.title("Casos por Cliente")
    if st.session_state.clients:
        client_names = [c['Nome'] for c in st.session_state.clients]
        client_selected = st.selectbox("Cliente", client_names)
        cases = [c for c in st.session_state.cases if c['Cliente'] == client_selected]
        st.subheader(f"Casos de {client_selected}")
        if cases:
            st.table(cases)
        else:
            st.info("Nenhum caso para este cliente")
    else:
        st.info("Nenhum cliente cadastrado")

elif menu == "Financeiro":
    st.title("Financeiro")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Registrar Receita"):
            st.session_state.show_add_income = not st.session_state.show_add_income
    with col2:
        if st.button("Registrar Despesa"):
            st.session_state.show_add_expense = not st.session_state.show_add_expense

    if st.session_state.show_add_income:
        with st.expander("Registrar Receita", expanded=True):
            with st.form("add_income"):
                category = st.text_input("Categoria *", value="Honorários")
                amount = st.number_input("Valor (R$) *", min_value=0.0, step=0.01)
                description = st.text_input("Descrição *")
                trans_date = st.date_input("Data *", value=date.today())
                payment_status = st.selectbox("Status Pagamento", ["Pendente", "Pago"])
                client = st.selectbox(
                    "Vincular ao Cliente",
                    ["Nenhum"] + [c['Nome'] for c in st.session_state.clients]
                )
                case = st.selectbox(
                    "Vincular ao Caso",
                    ["Nenhum"] + [c['Processo'] for c in st.session_state.cases]
                )
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    client_val = None if client == "Nenhum" else client
                    case_val = None if case == "Nenhum" else case
                    add_transaction(
                        "Receita",
                        category,
                        amount,
                        description,
                        trans_date,
                        payment_status,
                        client_val,
                        case_val,
                    )
                    st.success("Receita registrada")

    if st.session_state.show_add_expense:
        with st.expander("Registrar Despesa", expanded=True):
            with st.form("add_expense"):
                category = st.text_input("Categoria *", value="Honorários")
                amount = st.number_input("Valor (R$) *", min_value=0.0, step=0.01)
                description = st.text_input("Descrição *")
                trans_date = st.date_input("Data *", value=date.today())
                payment_status = st.selectbox("Status Pagamento", ["Pendente", "Pago"])
                client = st.selectbox(
                    "Vincular ao Cliente",
                    ["Nenhum"] + [c['Nome'] for c in st.session_state.clients]
                )
                case = st.selectbox(
                    "Vincular ao Caso",
                    ["Nenhum"] + [c['Processo'] for c in st.session_state.cases]
                )
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    client_val = None if client == "Nenhum" else client
                    case_val = None if case == "Nenhum" else case
                    add_transaction(
                        "Despesa",
                        category,
                        amount,
                        description,
                        trans_date,
                        payment_status,
                        client_val,
                        case_val,
                    )
                    st.success("Despesa registrada")

    st.subheader("Movimentos")
    if st.session_state.transactions:
        st.table(st.session_state.transactions)
    else:
        st.info("Nenhum movimento registrado")
    saldo = sum(t['Valor'] if t['Tipo'] == 'Entrada' else -t['Valor'] for t in st.session_state.transactions)
    st.write(f"**Saldo atual:** R$ {saldo:,.2f}")
