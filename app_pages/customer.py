"""Tela simulada de abertura de ticket pelo cliente."""

import streamlit as st

from core.agent import classify_ticket
from core.state import create_ticket


st.title("Abrir ticket", icon=":material/add_comment:")
st.caption("Simulação da jornada do cliente. O envio não cria um contato real.")

with st.form("customer_ticket_form"):
    ticket_text = st.text_area(
        "Como podemos ajudar?",
        placeholder="Ex.: Meu pedido está atrasado e preciso de uma atualização.",
        height=160,
    )
    submitted = st.form_submit_button("Enviar ticket", icon=":material/send:", type="primary")

if submitted:
    if not ticket_text.strip():
        st.info("Escreva uma mensagem antes de enviar.", icon=":material/info:")
    else:
        try:
            with st.spinner("Registrando e classificando ticket..."):
                ticket = create_ticket(ticket_text.strip(), classify_ticket(ticket_text.strip()))
            st.success(f"Ticket {ticket['ticket_id']} criado para demonstração.", icon=":material/check_circle:")
            if st.button("Ver atendimento", icon=":material/inbox:"):
                st.switch_page("app_pages/ticket_detail.py")
        except Exception as error:
            st.error(f"Não foi possível classificar o ticket: {error}", icon=":material/error:")
