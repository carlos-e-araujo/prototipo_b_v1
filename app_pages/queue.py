"""Fila operacional simulada para o atendente."""

import unicodedata

import streamlit as st

from core.state import all_tickets, select_ticket


PRIORITY_ORDER = {"alta": 0, "média": 1, "baixa": 2}
RISK_ORDER = {"alto": 0, "médio": 1, "baixo": 2}


def normalize(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()


def ticket_theme(ticket: dict) -> str:
    analysis = ticket.get("analise")
    return analysis["tema"] if analysis else ticket["tema_historico"]


def queue_rank(ticket: dict, criterion: str) -> tuple[int, str]:
    analysis = ticket.get("analise") or {}
    if criterion == "Maior prioridade":
        return PRIORITY_ORDER.get(analysis.get("prioridade", ""), 3), ticket["ticket_id"]
    if criterion == "Maior risco de churn":
        return RISK_ORDER.get(analysis.get("risco_de_churn", ""), 3), ticket["ticket_id"]
    return 0, ticket["ticket_id"]


st.title("Fila de atendimento", icon=":material/inbox:")
st.caption("Tickets sintéticos para demonstração; mudanças nesta tela existem somente na sessão atual.")

tickets = all_tickets()
statuses = ["Todos", "Aberto", "Em Análise", "Escalado para N2", "Resolvido"]
themes = ["Todos", *sorted({ticket_theme(ticket) for ticket in tickets})]
filters = st.columns(3)
with filters[0]:
    search_text = st.text_input(
        "Buscar ticket",
        placeholder="ID, tema ou trecho da mensagem",
        key="queue_search",
    )
with filters[1]:
    filter_status = st.selectbox("Status", statuses, key="queue_status")
with filters[2]:
    filter_theme = st.selectbox("Tema", themes, key="queue_theme")

sort_criterion = st.selectbox(
    "Ordenar por",
    ["Ordem da fila", "Maior prioridade", "Maior risco de churn"],
    key="queue_sort",
)

normalized_search = normalize(search_text.strip())
visible_tickets = [
    ticket
    for ticket in tickets
    if (filter_status == "Todos" or ticket["status"] == filter_status)
    and (filter_theme == "Todos" or ticket_theme(ticket) == filter_theme)
    and (
        not normalized_search
        or normalized_search
        in normalize(
            " ".join(
                [
                    ticket["ticket_id"],
                    ticket_theme(ticket),
                    ticket["texto_cliente"],
                ]
            )
        )
    )
]
if sort_criterion != "Ordem da fila":
    visible_tickets = sorted(visible_tickets, key=lambda ticket: queue_rank(ticket, sort_criterion))

metrics = st.columns(4)
for column, status in zip(metrics, statuses[1:]):
    column.metric(status, sum(ticket["status"] == status for ticket in tickets))

if not visible_tickets:
    st.info("Não há tickets neste status.", icon=":material/inbox:")
else:
    st.caption(f"{len(visible_tickets)} ticket(s) encontrado(s).")

for ticket in visible_tickets:
    analysis = ticket["analise"]
    with st.container(border=True):
        st.subheader(ticket["ticket_id"])
        st.caption(f"{ticket['origem']} · Status: {ticket['status']}")
        st.write(ticket["texto_cliente"])
        if analysis:
            st.write(f"**IA:** {analysis['tema']} · {analysis['prioridade']} prioridade · {analysis['acao_recomendada']}")
        else:
            st.caption(f"Tema histórico: {ticket['tema_historico']} · Análise da IA ainda não realizada.")
        if st.button("Abrir ticket", key=f"open_{ticket['ticket_id']}", icon=":material/visibility:"):
            select_ticket(ticket["ticket_id"])
            st.switch_page("app_pages/ticket_detail.py")
