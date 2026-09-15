"""Ponto de entrada do protótipo do Módulo B."""

import streamlit as st

from core.state import initialize_state


st.set_page_config(
    page_title="Vértice | Módulo B",
    page_icon=":material/support_agent:",
    layout="wide",
)

initialize_state()

page = st.navigation(
    [
        st.Page("app_pages/customer.py", title="Abrir ticket", icon=":material/add_comment:"),
        st.Page("app_pages/queue.py", title="Fila de atendimento", icon=":material/inbox:"),
        st.Page("app_pages/ticket_detail.py", title="Detalhe do ticket", icon=":material/confirmation_number:"),
    ],
    position="top",
)

st.caption("Vértice Retail · Módulo B · Ambiente demonstrativo sem ações externas")
page.run()
