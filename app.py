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

menu = st.sidebar.selectbox(
    "Menu",[
        "Visão Geral",
        "Clientes",
        "Casos",
        "Agenda",
        "Tarefas",
        "Casos por Cliente",
        "Financeiro"
    ]
)

# Funções auxiliares

def add_client(name, email, phone):
    st.session_state.clients.append({"Nome": name, "Email": email, "Telefone": phone})

def add_case(title, client, description, status, start_date):
    st.session_state.cases.append({
        "Título": title,
        "Cliente": client,
        "Descrição": description,
        "Status": status,
        "Data de início": start_date
    })

def add_task(title, due_date, related_case, status):
    st.session_state.tasks.append({
        "Título": title,
        "Data limite": due_date,
        "Caso": related_case,
        "Status": status
    })

def add_event(title, event_date, description):
    st.session_state.events.append({
        "Título": title,
        "Data": event_date,
        "Descrição": description
    })

def add_transaction(kind, amount, description, trans_date):
    st.session_state.transactions.append({
        "Tipo": kind,
        "Valor": amount,
        "Descrição": description,
        "Data": trans_date
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
    with st.form("add_client"):
        st.subheader("Adicionar Cliente")
        name = st.text_input("Nome")
        email = st.text_input("Email")
        phone = st.text_input("Telefone")
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            add_client(name, email, phone)
            st.success("Cliente adicionado")
    st.subheader("Lista de Clientes")
    if st.session_state.clients:
        st.table(st.session_state.clients)
    else:
        st.info("Nenhum cliente cadastrado")

elif menu == "Casos":
    st.title("Casos")
    with st.form("add_case"):
        st.subheader("Adicionar Caso")
        title = st.text_input("Título")
        client = st.selectbox("Cliente", [c['Nome'] for c in st.session_state.clients]) if st.session_state.clients else st.text_input("Cliente")
        description = st.text_area("Descrição")
        status = st.selectbox("Status", ["Aberto", "Em andamento", "Fechado"])
        start_date = st.date_input("Data de início", value=date.today())
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            add_case(title, client, description, status, start_date)
            st.success("Caso adicionado")
    st.subheader("Lista de Casos")
    if st.session_state.cases:
        st.table(st.session_state.cases)
    else:
        st.info("Nenhum caso cadastrado")

elif menu == "Agenda":
    st.title("Agenda")
    with st.form("add_event"):
        st.subheader("Adicionar Evento")
        title = st.text_input("Título")
        event_date = st.date_input("Data", value=date.today())
        description = st.text_area("Descrição")
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            add_event(title, event_date, description)
            st.success("Evento adicionado")
    st.subheader("Eventos")
    if st.session_state.events:
        st.table(st.session_state.events)
    else:
        st.info("Nenhum evento cadastrado")

elif menu == "Tarefas":
    st.title("Tarefas")
    with st.form("add_task"):
        st.subheader("Adicionar Tarefa")
        title = st.text_input("Título")
        due_date = st.date_input("Data limite", value=date.today())
        related_case = st.selectbox("Caso", [c['Título'] for c in st.session_state.cases]) if st.session_state.cases else st.text_input("Caso")
        status = st.selectbox("Status", ["Pendente", "Em andamento", "Concluída"])
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            add_task(title, due_date, related_case, status)
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
    with st.form("add_transaction"):
        st.subheader("Adicionar Movimento")
        kind = st.selectbox("Tipo", ["Entrada", "Saída"])
        amount = st.number_input("Valor", min_value=0.0, step=0.01)
        description = st.text_input("Descrição")
        trans_date = st.date_input("Data", value=date.today())
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            add_transaction(kind, amount, description, trans_date)
            st.success("Movimento adicionado")
    st.subheader("Movimentos")
    if st.session_state.transactions:
        st.table(st.session_state.transactions)
    else:
        st.info("Nenhum movimento registrado")
    saldo = sum(t['Valor'] if t['Tipo'] == 'Entrada' else -t['Valor'] for t in st.session_state.transactions)
    st.write(f"**Saldo atual:** R$ {saldo:,.2f}")
