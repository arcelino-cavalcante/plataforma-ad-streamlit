import streamlit as st
from datetime import datetime, date, time
from streamlit_option_menu import option_menu
import pandas as pd
from streamlit_calendar import calendar as calendar_component
from fpdf import FPDF
import io
from google_utils import append_rows, load_rows, upload_file

st.set_page_config(page_title="Painel para Advogados", layout="wide")


# Compatibilidade para diferentes versões do Streamlit
def rerun():
    """Rerun a aplicação de forma compatível com diferentes versões."""
    try:
        st.rerun()  # Streamlit 1.25+
    except Exception:
        # Fallback para versões antigas
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

# Carrega dados do Google Sheets se ainda não houver registros
if not any([
    st.session_state.clients,
    st.session_state.cases,
    st.session_state.tasks,
    st.session_state.events,
    st.session_state.transactions,
    st.session_state.documents,
]):
    try:
        st.session_state.clients = load_rows("Clientes")
        st.session_state.cases = load_rows("Casos")
        st.session_state.tasks = [
            {
                **t,
                "Prazo": pd.to_datetime(t.get("Prazo")).date()
                if t.get("Prazo")
                else None,
            }
            for t in load_rows("Tarefas")
        ]
        st.session_state.events = [
            {
                **e,
                "Data": pd.to_datetime(e.get("Data")),
            }
            for e in load_rows("Eventos")
        ]
        st.session_state.transactions = [
            {
                **tr,
                "Data": pd.to_datetime(tr.get("Data")).date()
                if tr.get("Data")
                else None,
            }
            for tr in load_rows("Movimentos")
        ]
        st.session_state.documents = load_rows("Documentos")
    except Exception:
        st.warning("Falha ao carregar dados do Google Sheets")


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
            "Relatórios",
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
            "file-earmark-arrow-down",
        ],
        default_index=0,
    )

# Funções auxiliares

CASE_STATUS_COLORS = {"Ativo": "green", "Encerrado": "red", "Suspenso": "orange"}
EVENT_STATUS_COLORS = {"Agendado": "blue", "Concluído": "green", "Cancelado": "red"}
TASK_PRIORITY_COLORS = {"Baixa": "green", "Média": "orange", "Alta": "red"}
PAYMENT_STATUS_COLORS = {"Pendente": "orange", "Pago": "green"}


def item_separator() -> None:
    """Render a horizontal rule with extra spacing."""
    st.markdown("<hr style='margin:25px 0'>", unsafe_allow_html=True)


def status_badge(status: str, mapping: dict) -> str:
    """Return HTML string for a colored status badge."""
    color = mapping.get(status, "gray")
    return f"<span style='color:{color}; font-weight:bold'>{status}</span>"


def dataframe_to_pdf(df: pd.DataFrame, title: str) -> bytes:
    """Generate a simple table PDF from dataframe."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=1, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", size=12)
    col_width = pdf.w / (len(df.columns) + 1)
    row_height = pdf.font_size * 1.5
    # Header
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln(row_height)
    # Rows
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item), border=1)
        pdf.ln(row_height)
    return pdf.output(dest="S").encode("latin-1")


def add_client(name, email, phone, notes):
    record = {
        "Nome": name,
        "Email": email,
        "Telefone": phone,
        "Anotações": notes,
    }
    st.session_state.clients.append(record)
    try:
        append_rows("Clientes", [[name, email, phone, notes]])
    except Exception:
        st.warning("Falha ao salvar cliente no Google Sheets")


def add_case(client, process_number, parties, lawyer, start_date, status):
    record = {
        "Cliente": client,
        "Processo": process_number,
        "Partes": parties,
        "Advogado": lawyer,
        "Data de Abertura": start_date,
        "Status": status,
    }
    st.session_state.cases.append(record)
    try:
        append_rows(
            "Casos",
            [[
                client,
                process_number,
                parties,
                lawyer,
                start_date.isoformat() if isinstance(start_date, (date, datetime)) else start_date,
                status,
            ]],
        )
    except Exception:
        st.warning("Falha ao salvar caso no Google Sheets")


def add_task(description, priority, due_date, client, related_case):
    record = {
        "Descrição": description,
        "Prioridade": priority,
        "Prazo": due_date,
        "Cliente": client,
        "Caso": related_case,
    }
    st.session_state.tasks.append(record)
    try:
        append_rows(
            "Tarefas",
            [[
                description,
                priority,
                due_date.isoformat() if isinstance(due_date, (date, datetime)) else due_date,
                client,
                related_case,
            ]],
        )
    except Exception:
        st.warning("Falha ao salvar tarefa no Google Sheets")


def add_event(
    title, event_type, event_datetime, location, client, case, status, description
):
    record = {
        "Título": title,
        "Tipo": event_type,
        "Data": event_datetime,
        "Local": location,
        "Cliente": client,
        "Caso": case,
        "Status": status,
        "Descrição": description,
    }
    st.session_state.events.append(record)
    try:
        append_rows(
            "Eventos",
            [[
                title,
                event_type,
                event_datetime.isoformat()
                if isinstance(event_datetime, (date, datetime))
                else str(event_datetime),
                location,
                client,
                case,
                status,
                description,
            ]],
        )
    except Exception:
        st.warning("Falha ao salvar evento no Google Sheets")


def add_transaction(
    kind, category, amount, description, trans_date, payment_status, client, case
):
    record = {
        "Tipo": kind,
        "Categoria": category,
        "Valor": amount,
        "Descrição": description,
        "Data": trans_date,
        "Status": payment_status,
        "Cliente": client,
        "Caso": case,
    }
    st.session_state.transactions.append(record)
    try:
        append_rows(
            "Movimentos",
            [[
                kind,
                category,
                amount,
                description,
                trans_date.isoformat() if isinstance(trans_date, (date, datetime)) else trans_date,
                payment_status,
                client,
                case,
            ]],
        )
    except Exception:
        st.warning("Falha ao salvar movimento no Google Sheets")


def add_document(client, case, title, file):
    link = ""
    if file is not None:
        try:
            link = upload_file(file.read(), file.name, client)
        except Exception:
            st.warning("Falha ao enviar arquivo ao Google Drive")
    record = {
        "Cliente": client,
        "Caso": case,
        "Título": title,
        "Arquivo": link or (file.name if file else ""),
    }
    st.session_state.documents.append(record)
    try:
        append_rows(
            "Documentos",
            [[client, case, title, record["Arquivo"]]],
        )
    except Exception:
        st.warning("Falha ao salvar documento no Google Sheets")


# Dialogs for data entry
@st.dialog("Adicionar Cliente")
def dialog_add_client():
    name = st.text_input("Nome Completo *")
    email = st.text_input("E-mail")
    phone = st.text_input("Telefone")
    notes = st.text_area("Anotações / Preferências")
    if st.button("Salvar"):
        add_client(name, email, phone, notes)
        st.success("Cliente adicionado")
        st.rerun()


@st.dialog("Adicionar Caso", width="large")
def dialog_add_case():
    client = (
        st.selectbox("Cliente *", [c["Nome"] for c in st.session_state.clients])
        if st.session_state.clients
        else st.text_input("Cliente *")
    )
    process_number = st.text_input("Nº do Processo *")
    parties = st.text_area("Partes Envolvidas")
    lawyer = st.text_input("Advogado Responsável")
    start_date = st.date_input("Data de Abertura", value=date.today())
    status = st.selectbox("Status", ["Ativo", "Encerrado", "Suspenso"])
    if st.button("Salvar"):
        add_case(client, process_number, parties, lawyer, start_date, status)
        st.success("Caso adicionado")
        st.rerun()


@st.dialog("Anexar Documento", width="large")
def dialog_add_document():
    client = (
        st.selectbox("Cliente *", [c["Nome"] for c in st.session_state.clients])
        if st.session_state.clients
        else st.text_input("Cliente *")
    )
    case = st.selectbox(
        "Vincular ao Caso (opcional)",
        ["Nenhum"] + [c["Processo"] for c in st.session_state.cases],
    )
    title = st.text_input("Título / Descrição *")
    file = st.file_uploader("Arquivo *")
    if st.button("Salvar"):
        case_val = None if case == "Nenhum" else case
        add_document(client, case_val, title, file)
        st.success("Documento anexado")
        st.rerun()


@st.dialog("Adicionar Evento", width="large")
def dialog_add_event():
    title = st.text_input("Título *")
    event_type = st.selectbox("Tipo de Evento *", ["Audiência", "Prazo", "Reunião"])
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
    if st.button("Salvar"):
        client_val = None if client == "Nenhum" else client
        case_val = None if case == "Nenhum" else case
        if isinstance(event_day, datetime):
            event_day = event_day.date()
        if isinstance(event_time, datetime):
            event_time = event_time.time()
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
        st.rerun()


@st.dialog("Adicionar Tarefa")
def dialog_add_task():
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
    if st.button("Salvar"):
        client_val = None if client == "Nenhum" else client
        case_val = None if related_case == "Nenhum" else related_case
        add_task(description, priority, due_date, client_val, case_val)
        st.success("Tarefa adicionada")
        st.rerun()


@st.dialog("Registrar Receita")
def dialog_add_income():
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
    if st.button("Salvar"):
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
        st.rerun()


@st.dialog("Registrar Despesa")
def dialog_add_expense():
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
    if st.button("Salvar"):
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
        st.rerun()


# Dialogs for editing existing records
@st.dialog("Editar Cliente", width="large")
def dialog_edit_client(idx: int):
    c = st.session_state.clients[idx]
    name = st.text_input("Nome Completo *", value=c["Nome"])
    email = st.text_input("E-mail", value=c["Email"])
    phone = st.text_input("Telefone", value=c["Telefone"])
    notes = st.text_area("Anotações / Preferências", value=c["Anotações"])
    if st.button("Salvar"):
        st.session_state.clients[idx] = {
            "Nome": name,
            "Email": email,
            "Telefone": phone,
            "Anotações": notes,
        }
        st.session_state.edit_client_idx = None
        st.success("Cliente atualizado")
        rerun()


@st.dialog("Editar Caso", width="large")
def dialog_edit_case(idx: int):
    c = st.session_state.cases[idx]
    client = st.text_input("Cliente *", value=c["Cliente"])
    process_number = st.text_input("Nº do Processo *", value=c["Processo"])
    parties = st.text_area("Partes Envolvidas", value=c["Partes"])
    lawyer = st.text_input("Advogado Responsável", value=c["Advogado"])
    start_date = st.date_input("Data de Abertura", value=c["Data de Abertura"])
    status = st.selectbox(
        "Status",
        ["Ativo", "Encerrado", "Suspenso"],
        index=["Ativo", "Encerrado", "Suspenso"].index(c["Status"]),
    )
    if st.button("Salvar"):
        st.session_state.cases[idx] = {
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


@st.dialog("Editar Documento", width="large")
def dialog_edit_document(idx: int):
    d = st.session_state.documents[idx]
    client = st.text_input("Cliente *", value=d["Cliente"])
    case = st.text_input("Caso", value=d["Caso"] or "")
    title = st.text_input("Título / Descrição *", value=d["Título"])
    if st.button("Salvar"):
        st.session_state.documents[idx] = {
            "Cliente": client,
            "Caso": case if case else None,
            "Título": title,
            "Arquivo": d.get("Arquivo", ""),
        }
        st.session_state.edit_document_idx = None
        st.success("Documento atualizado")
        rerun()


@st.dialog("Editar Evento", width="large")
def dialog_edit_event(idx: int):
    ev = st.session_state.events[idx]
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
    if st.button("Salvar"):
        dt = datetime.combine(event_day, event_time)
        st.session_state.events[idx] = {
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


@st.dialog("Editar Tarefa", width="large")
def dialog_edit_task(idx: int):
    t = st.session_state.tasks[idx]
    description = st.text_input("Descrição *", value=t["Descrição"])
    priority = st.selectbox(
        "Prioridade",
        ["Baixa", "Média", "Alta"],
        index=["Baixa", "Média", "Alta"].index(t["Prioridade"]),
    )
    due_date = st.date_input("Data do Prazo", value=t["Prazo"])
    client = st.text_input("Cliente", value=t["Cliente"] or "")
    related_case = st.text_input("Caso", value=t["Caso"] or "")
    if st.button("Salvar"):
        st.session_state.tasks[idx] = {
            "Descrição": description,
            "Prioridade": priority,
            "Prazo": due_date,
            "Cliente": client if client else None,
            "Caso": related_case if related_case else None,
        }
        st.session_state.edit_task_idx = None
        st.success("Tarefa atualizada")
        rerun()


# Páginas
if menu == "Visão Geral":
    st.title("Painel Geral")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clientes", len(st.session_state.clients))
    col2.metric("Casos", len(st.session_state.cases))
    col3.metric("Tarefas", len(st.session_state.tasks))
    saldo = sum(
        t["Valor"] if t["Tipo"] == "Receita" else -t["Valor"]
        for t in st.session_state.transactions
    )
    col4.metric("Saldo", f"R$ {saldo:,.2f}")
    st.subheader("Calendário")
    calendar_events = []
    for idx, e in enumerate(st.session_state.events):
        calendar_events.append(
            {
                "title": f"{e['Título']} ({e['Tipo']})",
                "start": e["Data"].isoformat(),
                "color": EVENT_STATUS_COLORS.get(e["Status"], "gray"),
                "extendedProps": {"type": "event", "index": idx},
            }
        )
    for idx, t in enumerate(st.session_state.tasks):
        calendar_events.append(
            {
                "title": f"Tarefa: {t['Descrição']}",
                "start": t["Prazo"].isoformat(),
                "allDay": True,
                "color": TASK_PRIORITY_COLORS.get(t["Prioridade"], "gray"),
                "extendedProps": {"type": "task", "index": idx},
            }
        )

    cal_state = calendar_component(
        events=calendar_events,
        options={
            "initialView": "dayGridMonth",
            "locale": "pt-br",
            "height": 500,
        },
        key="overview_calendar",
        callbacks=["eventClick"],
    )

    if cal_state.get("eventClick"):
        props = cal_state["eventClick"]["event"].get("extendedProps", {})
        idx = props.get("index")
        if props.get("type") == "event" and idx is not None:
            dialog_edit_event(idx)
        elif props.get("type") == "task" and idx is not None:
            dialog_edit_task(idx)
    st.subheader("Próximos eventos")
    if st.session_state.events:
        upcoming = sorted(st.session_state.events, key=lambda x: x["Data"])[:5]
        for e in upcoming:
            status_html = status_badge(e["Status"], EVENT_STATUS_COLORS)
            st.markdown(
                f"**{e['Título']}** - {e['Data'].strftime('%d/%m/%Y %H:%M')} | {status_html}",
                unsafe_allow_html=True,
            )
    else:
        st.info("Nenhum evento cadastrado")

elif menu == "Clientes":
    st.title("Clientes")
    if st.button("Adicionar Cliente"):
        dialog_add_client()
    st.subheader("Lista de Clientes")
    search_client = st.text_input("Buscar", key="search_client")
    clients_filtered = [
        c
        for c in st.session_state.clients
        if search_client.lower() in c["Nome"].lower()
    ]
    if clients_filtered:
        for c in clients_filtered:
            idx = st.session_state.clients.index(c)
            item_separator()
            st.write(f"**{c['Nome']}**")
            st.write(f"Email: {c['Email']} | Telefone: {c['Telefone']}")
            if c.get("Anotações"):
                st.write(c["Anotações"])
            col1, col2 = st.columns(2)
            if col1.button("Editar", key=f"edit_client_{idx}"):
                st.session_state.edit_client_idx = idx
                rerun()
            if col2.button("Excluir", key=f"del_client_{idx}"):
                del st.session_state.clients[idx]
                rerun()
    else:
        st.info("Nenhum cliente cadastrado")

    edit_idx = st.session_state.get("edit_client_idx")
    if edit_idx is not None and 0 <= edit_idx < len(st.session_state.clients):
        dialog_edit_client(edit_idx)
    elif edit_idx is not None:
        st.session_state.edit_client_idx = None
        rerun()

elif menu == "Casos":
    st.title("Casos")
    if st.button("Adicionar Caso"):
        dialog_add_case()
    st.subheader("Lista de Casos")
    search_case = st.text_input("Buscar", key="search_case")
    statuses = ["Todos"] + sorted(list({c["Status"] for c in st.session_state.cases}))
    status_filter = st.selectbox("Filtrar por Status", statuses, key="status_case")
    edit_idx = st.session_state.get("edit_case_idx")
    if edit_idx is not None and 0 <= edit_idx < len(st.session_state.cases):
        dialog_edit_case(edit_idx)
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
            item_separator()
            status_html = status_badge(c["Status"], CASE_STATUS_COLORS)
            st.markdown(
                f"**Processo:** {c['Processo']} - Cliente: {c['Cliente']}"
            )
            st.markdown(
                f"Status: {status_html} | Advogado: {c['Advogado']}",
                unsafe_allow_html=True,
            )
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
        dialog_add_document()
    st.subheader("Documentos")
    search_doc = st.text_input("Buscar", key="search_document")
    edit_idx = st.session_state.get("edit_document_idx")
    if edit_idx is not None and 0 <= edit_idx < len(st.session_state.documents):
        dialog_edit_document(edit_idx)
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
            item_separator()
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
        dialog_add_event()
    st.subheader("Eventos")
    search_event = st.text_input("Buscar", key="search_event")
    statuses_evt = ["Todos"] + sorted(
        list({e["Status"] for e in st.session_state.events})
    )
    status_filter_evt = st.selectbox("Status", statuses_evt, key="status_event")
    edit_idx = st.session_state.get("edit_event_idx")
    if edit_idx is not None and 0 <= edit_idx < len(st.session_state.events):
        dialog_edit_event(edit_idx)
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
            item_separator()
            status_html = status_badge(e["Status"], EVENT_STATUS_COLORS)
            st.write(f"**{e['Título']}** - {e['Data'].strftime('%d/%m/%Y %H:%M')}")
            st.markdown(
                f"Tipo: {e['Tipo']} | Status: {status_html}", unsafe_allow_html=True
            )
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
        dialog_add_task()
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
        dialog_edit_task(edit_idx)
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
            item_separator()
            priority_html = status_badge(t["Prioridade"], TASK_PRIORITY_COLORS)
            st.markdown(
                f"**{t['Descrição']}** - Prioridade: {priority_html}",
                unsafe_allow_html=True,
            )
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
            for c in cases:
                item_separator()
                status_html = status_badge(c["Status"], CASE_STATUS_COLORS)
                col1, col2 = st.columns(2)
                col1.write(f"Processo: {c['Processo']}")
                col2.markdown(f"Status: {status_html}", unsafe_allow_html=True)
                st.write(f"Advogado: {c['Advogado']} | Abertura: {c['Data de Abertura']}")
                if c.get("Partes"):
                    st.write(c["Partes"])
        else:
            st.info("Nenhum caso para este cliente")
    else:
        st.info("Nenhum cliente cadastrado")

elif menu == "Financeiro":
    st.title("Financeiro")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Registrar Receita"):
            dialog_add_income()
    with col2:
        if st.button("Registrar Despesa"):
            dialog_add_expense()

    st.subheader("Movimentos")
    if st.session_state.transactions:
        for t in st.session_state.transactions:
            item_separator()
            status_html = status_badge(t["Status"], PAYMENT_STATUS_COLORS)
            st.markdown(
                f"**{t['Tipo']}** - R$ {t['Valor']:.2f} | {status_html}",
                unsafe_allow_html=True,
            )
            st.write(
                f"{t['Categoria']} | {t['Data']} | Cliente: {t['Cliente']} | Caso: {t['Caso']}"
            )
            st.write(t["Descrição"])
    else:
        st.info("Nenhum movimento registrado")
    saldo = sum(
        t["Valor"] if t["Tipo"] == "Receita" else -t["Valor"]
        for t in st.session_state.transactions
    )
    st.write(f"**Saldo atual:** R$ {saldo:,.2f}")

elif menu == "Relatórios":
    st.title("Relatórios")
    st.write("Exporte listagens para compartilhar com clientes ou colegas.")

    report_type = st.selectbox(
        "Tipo de relatório",
        ["Casos", "Documentos", "Movimentos Financeiros"],
    )

    data_map = {
        "Casos": st.session_state.cases,
        "Documentos": st.session_state.documents,
        "Movimentos Financeiros": st.session_state.transactions,
    }
    data = data_map.get(report_type, [])

    if data:
        df = pd.DataFrame(data)

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        st.download_button(
            "Baixar Excel",
            data=excel_buffer.getvalue(),
            file_name=f"{report_type}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        pdf_bytes = dataframe_to_pdf(df, report_type)
        st.download_button(
            "Baixar PDF",
            data=pdf_bytes,
            file_name=f"{report_type}.pdf",
            mime="application/pdf",
        )
    else:
        st.info("Nenhum dado disponível para este relatório")
