import streamlit as st
from datetime import datetime, date
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Painel para Advogados", layout="wide")


# Compatibilidade para diferentes versões do Streamlit
def rerun():
    """Rerun a aplicação usando a API disponível."""
    if hasattr(st, "rerun"):
        st.rerun()
    else:  # versões antigas
        st.experimental_rerun()


# Inicializa estados
if "clients" not in st.session_state:
    st.session_state.clients = []
if "cases" not in st.session_state:
    st.session_state.cases = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "events" not in st.session_state:
    st.session_state.events = []
if "transactions" not in st.session_state:
    st.session_state.transactions = []
if "documents" not in st.session_state:
    st.session_state.documents = []

if "show_add_client" not in st.session_state:
    st.session_state.show_add_client = False
if "show_add_case" not in st.session_state:
    st.session_state.show_add_case = False
if "show_add_task" not in st.session_state:
    st.session_state.show_add_task = False
if "show_add_event" not in st.session_state:
    st.session_state.show_add_event = False
if "show_add_transaction" not in st.session_state:
    st.session_state.show_add_transaction = False
if "show_add_document" not in st.session_state:
    st.session_state.show_add_document = False
if "show_add_income" not in st.session_state:
    st.session_state.show_add_income = False
if "show_add_expense" not in st.session_state:
    st.session_state.show_add_expense = False

with st.sidebar:
    menu = option_menu(
        "Menu",
        [
            "Visão Geral",
            "Clientes",
            "Casos",
            "Documentos",
            "Agenda",
            "Tarefas",
            "Casos por Cliente",
            "Financeiro",
        ],
        icons=[
            "speedometer",
            "people",
            "folder",
            "file-earmark",
            "calendar",
            "check2-circle",
            "list-ol",
            "currency-dollar",
        ],
        default_index=0,
    )

# Funções auxiliares


def add_client(name, email, phone, notes):
    st.session_state.clients.append(
        {
            "Nome": name,
            "Email": email,
            "Telefone": phone,
            "Anotações": notes,
        }
    )


def add_case(client, process_number, parties, lawyer, start_date, status):
    st.session_state.cases.append(
        {
            "Cliente": client,
            "Processo": process_number,
            "Partes": parties,
            "Advogado": lawyer,
            "Data de Abertura": start_date,
            "Status": status,
        }
    )


def add_task(description, priority, due_date, client, related_case):
    st.session_state.tasks.append(
        {
            "Descrição": description,
            "Prioridade": priority,
            "Prazo": due_date,
            "Cliente": client,
            "Caso": related_case,
        }
    )


def add_event(
    title, event_type, event_datetime, location, client, case, status, description
):
    st.session_state.events.append(
        {
            "Título": title,
            "Tipo": event_type,
            "Data": event_datetime,
            "Local": location,
            "Cliente": client,
            "Caso": case,
            "Status": status,
            "Descrição": description,
        }
    )


def add_transaction(
    kind, category, amount, description, trans_date, payment_status, client, case
):
    st.session_state.transactions.append(
        {
            "Tipo": kind,
            "Categoria": category,
            "Valor": amount,
            "Descrição": description,
            "Data": trans_date,
            "Status": payment_status,
            "Cliente": client,
            "Caso": case,
        }
    )


def add_document(client, case, title, file):
    st.session_state.documents.append(
        {
            "Cliente": client,
            "Caso": case,
            "Título": title,
            "Arquivo": file.name if file else "",
        }
    )


# Páginas
if menu == "Visão Geral":
    st.title("Painel Geral")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clientes", len(st.session_state.clients))
    col2.metric("Casos", len(st.session_state.cases))
    col3.metric("Tarefas", len(st.session_state.tasks))
    saldo = sum(
        t["Valor"] if t["Tipo"] == "Entrada" else -t["Valor"]
        for t in st.session_state.transactions
    )
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
    search_client = st.text_input("Buscar", key="search_client")
    edit_idx = st.session_state.get("edit_client_idx")
    if edit_idx is not None and 0 <= edit_idx < len(st.session_state.clients):
        c = st.session_state.clients[edit_idx]
        with st.expander("Editar Cliente", expanded=True):
            with st.form("edit_client"):
                name = st.text_input("Nome Completo *", value=c["Nome"])
                email = st.text_input("E-mail", value=c["Email"])
                phone = st.text_input("Telefone", value=c["Telefone"])
                notes = st.text_area("Anotações / Preferências", value=c["Anotações"])
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    st.session_state.clients[edit_idx] = {
                        "Nome": name,
                        "Email": email,
                        "Telefone": phone,
                        "Anotações": notes,
                    }
                    st.session_state.edit_client_idx = None
                    st.success("Cliente atualizado")
                    rerun()
    elif edit_idx is not None:
        st.session_state.edit_client_idx = None
        rerun()

    filtered_clients = [
        c
        for c in st.session_state.clients
        if search_client.lower() in c["Nome"].lower()
    ]
    if filtered_clients:
        for c in filtered_clients:
            orig = st.session_state.clients.index(c)
            st.markdown("---")
            st.write(f"**{c['Nome']}**")
            st.write(f"Email: {c['Email']}  Telefone: {c['Telefone']}")
            if c.get("Anotações"):
                st.write(c["Anotações"])
            col1, col2 = st.columns(2)
            if col1.button("Editar", key=f"edit_client_{orig}"):
                st.session_state.edit_client_idx = orig
                rerun()
            if col2.button("Excluir", key=f"del_client_{orig}"):
                del st.session_state.clients[orig]
                rerun()
    else:
        st.info("Nenhum cliente cadastrado")

elif menu == "Casos":
    st.title("Casos")
    if st.button("Adicionar Caso"):
        st.session_state.show_add_case = not st.session_state.show_add_case
    if st.session_state.show_add_case:
        with st.expander("Adicionar Caso", expanded=True):
            with st.form("add_case"):
                client = (
                    st.selectbox(
                        "Cliente *", [c["Nome"] for c in st.session_state.clients]
                    )
                    if st.session_state.clients
                    else st.text_input("Cliente *")
                )
                process_number = st.text_input("Nº do Processo *")
                parties = st.text_area("Partes Envolvidas")
                lawyer = st.text_input("Advogado Responsável")
                start_date = st.date_input("Data de Abertura", value=date.today())
                status = st.selectbox("Status", ["Ativo", "Encerrado", "Suspenso"])
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    add_case(
                        client, process_number, parties, lawyer, start_date, status
                    )
                    st.success("Caso adicionado")
    st.subheader("Lista de Casos")
    search_case = st.text_input("Buscar", key="search_case")
    statuses = ["Todos"] + sorted(list({c["Status"] for c in st.session_state.cases}))
    status_filter = st.selectbox("Filtrar por Status", statuses, key="status_case")
    edit_idx = st.session_state.get("edit_case_idx")
    if edit_idx is not None and 0 <= edit_idx < len(st.session_state.cases):
        c = st.session_state.cases[edit_idx]
        with st.expander("Editar Caso", expanded=True):
            with st.form("edit_case"):
                client = st.text_input("Cliente *", value=c["Cliente"])
                process_number = st.text_input("Nº do Processo *", value=c["Processo"])
                parties = st.text_area("Partes Envolvidas", value=c["Partes"])
                lawyer = st.text_input("Advogado Responsável", value=c["Advogado"])
                start_date = st.date_input(
                    "Data de Abertura", value=c["Data de Abertura"]
                )
                status = st.selectbox(
                    "Status",
                    ["Ativo", "Encerrado", "Suspenso"],
                    index=["Ativo", "Encerrado", "Suspenso"].index(c["Status"]),
                )
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    st.session_state.cases[edit_idx] = {
                        "Cliente": client,
                        "Processo": process_number,
                        "Partes": parties,
                        "Advogado": lawyer,
                        "Data de Abertura": start_date,
                        "Status": status,
                    }
                    st.session_state.edit_case_idx = None
                    st.success("Caso atualizado")
                    rerun()
    elif edit_idx is not None:
        st.session_state.edit_case_idx = None
        rerun()

    filtered_cases = [
        c
        for c in st.session_state.cases
        if search_case.lower() in c["Processo"].lower()
        or search_case.lower() in c["Cliente"].lower()
    ]
    if status_filter != "Todos":
        filtered_cases = [c for c in filtered_cases if c["Status"] == status_filter]
    if filtered_cases:
        for c in filtered_cases:
            orig = st.session_state.cases.index(c)
            st.markdown("---")
            st.write(f"**Processo:** {c['Processo']} - Cliente: {c['Cliente']}")
            st.write(f"Status: {c['Status']} | Advogado: {c['Advogado']}")
            st.write(f"Data de Abertura: {c['Data de Abertura']}")
            if c.get("Partes"):
                st.write(c["Partes"])
            col1, col2 = st.columns(2)
            if col1.button("Editar", key=f"edit_case_{orig}"):
                st.session_state.edit_case_idx = orig
                rerun()
            if col2.button("Excluir", key=f"del_case_{orig}"):
                del st.session_state.cases[orig]
                rerun()
    else:
        st.info("Nenhum caso cadastrado")

elif menu == "Documentos":
    st.title("Documentos")
    if st.button("Anexar Documento"):
        st.session_state.show_add_document = not st.session_state.show_add_document
    if st.session_state.show_add_document:
        with st.expander("Anexar Documento", expanded=True):
            with st.form("add_document"):
                client = (
                    st.selectbox(
                        "Cliente *", [c["Nome"] for c in st.session_state.clients]
                    )
                    if st.session_state.clients
                    else st.text_input("Cliente *")
                )
                case = st.selectbox(
                    "Vincular ao Caso (opcional)",
                    ["Nenhum"] + [c["Processo"] for c in st.session_state.cases],
                )
                title = st.text_input("Título / Descrição *")
                file = st.file_uploader("Arquivo *")
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    case_val = None if case == "Nenhum" else case
                    add_document(client, case_val, title, file)
                    st.success("Documento anexado")
    st.subheader("Documentos")
    search_doc = st.text_input("Buscar", key="search_document")
    edit_idx = st.session_state.get("edit_document_idx")
    if edit_idx is not None and 0 <= edit_idx < len(st.session_state.documents):
        d = st.session_state.documents[edit_idx]
        with st.expander("Editar Documento", expanded=True):
            with st.form("edit_document"):
                client = st.text_input("Cliente *", value=d["Cliente"])
                case = st.text_input("Caso", value=d["Caso"] or "")
                title = st.text_input("Título / Descrição *", value=d["Título"])
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    st.session_state.documents[edit_idx] = {
                        "Cliente": client,
                        "Caso": case if case else None,
                        "Título": title,
                        "Arquivo": d.get("Arquivo", ""),
                    }
                    st.session_state.edit_document_idx = None
                    st.success("Documento atualizado")
                    rerun()
    elif edit_idx is not None:
        st.session_state.edit_document_idx = None
        rerun()

    filtered_docs = [
        d
        for d in st.session_state.documents
        if search_doc.lower() in d["Título"].lower()
    ]
    if filtered_docs:
        for d in filtered_docs:
            orig = st.session_state.documents.index(d)
            st.markdown("---")
            st.write(f"**{d['Título']}**")
            st.write(f"Cliente: {d['Cliente']} | Caso: {d['Caso']}")
            col1, col2 = st.columns(2)
            if col1.button("Editar", key=f"edit_doc_{orig}"):
                st.session_state.edit_document_idx = orig
                rerun()
            if col2.button("Excluir", key=f"del_doc_{orig}"):
                del st.session_state.documents[orig]
                rerun()
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
                event_type = st.selectbox(
                    "Tipo de Evento *", ["Audiência", "Prazo", "Reunião"]
                )
                event_day = st.date_input("Data *", value=date.today())
                event_time = st.time_input("Hora *", value=datetime.now().time())
                location = st.text_input("Local / Link")
                client = st.selectbox(
                    "Vincular ao Cliente",
                    ["Nenhum"] + [c["Nome"] for c in st.session_state.clients],
                )
                case = st.selectbox(
                    "Vincular ao Caso",
                    ["Nenhum"] + [c["Processo"] for c in st.session_state.cases],
                )
                status = st.selectbox("Status", ["Agendado", "Concluído", "Cancelado"])
                description = st.text_area("Descrição")
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    client_val = None if client == "Nenhum" else client
                    case_val = None if case == "Nenhum" else case
                    dt = datetime.combine(event_day, event_time)
                    add_event(
                        title,
                        event_type,
                        dt,
                        location,
                        client_val,
                        case_val,
                        status,
                        description,
                    )
                    st.success("Evento adicionado")
    st.subheader("Eventos")
    search_event = st.text_input("Buscar", key="search_event")
    statuses_evt = ["Todos"] + sorted(
        list({e["Status"] for e in st.session_state.events})
    )
    status_filter_evt = st.selectbox("Status", statuses_evt, key="status_event")
    edit_idx = st.session_state.get("edit_event_idx")
    if edit_idx is not None and 0 <= edit_idx < len(st.session_state.events):
        ev = st.session_state.events[edit_idx]
        with st.expander("Editar Evento", expanded=True):
            with st.form("edit_event"):
                title = st.text_input("Título *", value=ev["Título"])
                event_type = st.selectbox(
                    "Tipo de Evento *",
                    ["Audiência", "Prazo", "Reunião"],
                    index=["Audiência", "Prazo", "Reunião"].index(ev["Tipo"]),
                )
                event_day = st.date_input("Data *", value=ev["Data"].date())
                event_time = st.time_input("Hora *", value=ev["Data"].time())
                location = st.text_input("Local / Link", value=ev["Local"])
                client = st.text_input("Cliente", value=ev["Cliente"] or "")
                case = st.text_input("Caso", value=ev["Caso"] or "")
                status = st.selectbox(
                    "Status",
                    ["Agendado", "Concluído", "Cancelado"],
                    index=["Agendado", "Concluído", "Cancelado"].index(ev["Status"]),
                )
                description = st.text_area("Descrição", value=ev["Descrição"])
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    dt = datetime.combine(event_day, event_time)
                    st.session_state.events[edit_idx] = {
                        "Título": title,
                        "Tipo": event_type,
                        "Data": dt,
                        "Local": location,
                        "Cliente": client if client else None,
                        "Caso": case if case else None,
                        "Status": status,
                        "Descrição": description,
                    }
                    st.session_state.edit_event_idx = None
                    st.success("Evento atualizado")
                    rerun()
    elif edit_idx is not None:
        st.session_state.edit_event_idx = None
        rerun()

    filtered_events = [
        e
        for e in st.session_state.events
        if search_event.lower() in e["Título"].lower()
    ]
    if status_filter_evt != "Todos":
        filtered_events = [
            e for e in filtered_events if e["Status"] == status_filter_evt
        ]
    if filtered_events:
        for e in filtered_events:
            orig = st.session_state.events.index(e)
            st.markdown("---")
            st.write(f"**{e['Título']}** - {e['Data'].strftime('%d/%m/%Y %H:%M')}")
            st.write(f"Tipo: {e['Tipo']} | Status: {e['Status']}")
            st.write(f"Local: {e['Local']}")
            col1, col2 = st.columns(2)
            if col1.button("Editar", key=f"edit_event_{orig}"):
                st.session_state.edit_event_idx = orig
                rerun()
            if col2.button("Excluir", key=f"del_event_{orig}"):
                del st.session_state.events[orig]
                rerun()
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
                    ["Nenhum"] + [c["Nome"] for c in st.session_state.clients],
                )
                related_case = st.selectbox(
                    "Vincular ao Caso",
                    ["Nenhum"] + [c["Processo"] for c in st.session_state.cases],
                )
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    client_val = None if client == "Nenhum" else client
                    case_val = None if related_case == "Nenhum" else related_case
                    add_task(description, priority, due_date, client_val, case_val)
                    st.success("Tarefa adicionada")
    st.subheader("Lista de Tarefas")
    search_task = st.text_input("Buscar", key="search_task")
    apply_filter = st.checkbox("Filtrar por prazo", key="apply_due")
    due_filter = (
        st.date_input("Até", value=date.today(), key="filter_due")
        if apply_filter
        else None
    )
    edit_idx = st.session_state.get("edit_task_idx")
    if edit_idx is not None and 0 <= edit_idx < len(st.session_state.tasks):
        t = st.session_state.tasks[edit_idx]
        with st.expander("Editar Tarefa", expanded=True):
            with st.form("edit_task"):
                description = st.text_input("Descrição *", value=t["Descrição"])
                priority = st.selectbox(
                    "Prioridade",
                    ["Baixa", "Média", "Alta"],
                    index=["Baixa", "Média", "Alta"].index(t["Prioridade"]),
                )
                due_date = st.date_input("Data do Prazo", value=t["Prazo"])
                client = st.text_input("Cliente", value=t["Cliente"] or "")
                related_case = st.text_input("Caso", value=t["Caso"] or "")
                submitted = st.form_submit_button("Salvar")
                if submitted:
                    st.session_state.tasks[edit_idx] = {
                        "Descrição": description,
                        "Prioridade": priority,
                        "Prazo": due_date,
                        "Cliente": client if client else None,
                        "Caso": related_case if related_case else None,
                    }
                    st.session_state.edit_task_idx = None
                    st.success("Tarefa atualizada")
                    rerun()
    elif edit_idx is not None:
        st.session_state.edit_task_idx = None
        rerun()

    filtered_tasks = [
        t
        for t in st.session_state.tasks
        if search_task.lower() in t["Descrição"].lower()
    ]
    if due_filter:
        filtered_tasks = [t for t in filtered_tasks if t["Prazo"] <= due_filter]
    if filtered_tasks:
        for t in filtered_tasks:
            orig = st.session_state.tasks.index(t)
            st.markdown("---")
            st.write(f"**{t['Descrição']}** - Prioridade: {t['Prioridade']}")
            st.write(
                f"Prazo: {t['Prazo']} | Cliente: {t['Cliente']} | Caso: {t['Caso']}"
            )
            col1, col2 = st.columns(2)
            if col1.button("Editar", key=f"edit_task_{orig}"):
                st.session_state.edit_task_idx = orig
                rerun()
            if col2.button("Excluir", key=f"del_task_{orig}"):
                del st.session_state.tasks[orig]
                rerun()
    else:
        st.info("Nenhuma tarefa cadastrada")

elif menu == "Casos por Cliente":
    st.title("Casos por Cliente")
    if st.session_state.clients:
        client_names = [c["Nome"] for c in st.session_state.clients]
        client_selected = st.selectbox("Cliente", client_names)
        cases = [c for c in st.session_state.cases if c["Cliente"] == client_selected]
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
                    ["Nenhum"] + [c["Nome"] for c in st.session_state.clients],
                )
                case = st.selectbox(
                    "Vincular ao Caso",
                    ["Nenhum"] + [c["Processo"] for c in st.session_state.cases],
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
                    ["Nenhum"] + [c["Nome"] for c in st.session_state.clients],
                )
                case = st.selectbox(
                    "Vincular ao Caso",
                    ["Nenhum"] + [c["Processo"] for c in st.session_state.cases],
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
    saldo = sum(
        t["Valor"] if t["Tipo"] == "Entrada" else -t["Valor"]
        for t in st.session_state.transactions
    )
    st.write(f"**Saldo atual:** R$ {saldo:,.2f}")
