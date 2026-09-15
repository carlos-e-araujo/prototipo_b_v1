"""Detalhe e ações simuladas de um ticket."""

import streamlit as st

from core.agent import classify_ticket
from core.playbook import build_playbook
from core.reflection import generate_safe_draft
from core.state import get_ticket, register_reply, save_analysis, save_reflection, update_status


@st.dialog("Confirmar fechamento", icon=":material/task_alt:")
def confirm_close(ticket_id: str) -> None:
    current_ticket = get_ticket(ticket_id)
    if current_ticket is None:
        st.rerun()
    st.warning("O ticket será marcado como resolvido apenas nesta sessão demonstrativa.")
    with st.container(horizontal=True):
        if st.button("Cancelar", key=f"cancel_close_{ticket_id}"):
            st.rerun()
        if st.button(
            "Confirmar fechamento",
            key=f"confirm_close_{ticket_id}",
            icon=":material/task_alt:",
            type="primary",
        ):
            update_status(current_ticket, "Resolvido", "Fechamento simulado")
            st.rerun()


@st.dialog("Confirmar resposta automática", icon=":material/smart_toy:")
def confirm_automatic_reply(ticket_id: str) -> None:
    current_ticket = get_ticket(ticket_id)
    if current_ticket is None:
        st.rerun()
    response_key = f"reply_{ticket_id}"
    response_text = st.session_state.get(response_key, current_ticket["rascunho"])
    st.warning("A resposta será registrada como automática somente no histórico desta sessão.")
    st.caption("Nenhuma mensagem será enviada ao cliente.")
    with st.container(horizontal=True):
        if st.button("Cancelar", key=f"cancel_auto_{ticket_id}"):
            st.rerun()
        if st.button(
            "Confirmar registro",
            key=f"confirm_auto_{ticket_id}",
            icon=":material/smart_toy:",
            type="primary",
        ):
            register_reply(current_ticket, response_text, automated=True)
            st.rerun()


ticket = get_ticket(st.session_state.selected_ticket_id)
if ticket is None:
    st.title("Detalhe do ticket", icon=":material/confirmation_number:")
    st.info("Escolha um ticket na fila para ver seus detalhes.", icon=":material/info:")
    if st.button("Ir para a fila", icon=":material/inbox:"):
        st.switch_page("app_pages/queue.py")
    st.stop()

st.title(f"Ticket {ticket['ticket_id']}", icon=":material/confirmation_number:")
st.caption(f"{ticket['origem']} · Status atual: {ticket['status']}")
if st.button("Voltar para a fila", icon=":material/arrow_back:", type="tertiary"):
    st.switch_page("app_pages/queue.py")

with st.container(border=True):
    st.subheader("Mensagem do cliente")
    st.write(ticket["texto_cliente"])

analysis = ticket["analise"]
if analysis is None:
    if st.button("Analisar com IA", icon=":material/psychology:", type="primary"):
        try:
            with st.spinner("Analisando ticket..."):
                save_analysis(ticket, classify_ticket(ticket["texto_cliente"]))
            st.rerun()
        except Exception as error:
            st.error(f"Não foi possível analisar o ticket: {error}", icon=":material/error:")
else:
    st.subheader("Recomendação do Módulo B")
    left, right = st.columns(2)
    left.metric("Tema", analysis["tema"])
    right.metric("Prioridade", analysis["prioridade"])
    left.metric("Sentimento", analysis["sentimento"])
    right.metric("Risco de churn", analysis["risco_de_churn"])
    st.write("**Ação recomendada:**", analysis["acao_recomendada"])
    st.write("**Justificativa:**", analysis["justificativa"])

    playbook = build_playbook(analysis)
    with st.container(border=True):
        st.subheader("Próximo passo operacional", icon=":material/checklist:")
        st.write(f"**{playbook.title}**")
        for position, step in enumerate(playbook.steps, start=1):
            st.write(f"{position}. {step}")
        st.caption(playbook.note)
        if playbook.requires_human_review:
            st.warning("Este caso exige revisão humana antes de qualquer resposta.", icon=":material/person_alert:")
        else:
            st.info("O atendente pode decidir se usa um rascunho como apoio.", icon=":material/info:")

    with st.container(horizontal=True):
        can_generate_draft = not playbook.requires_human_review and analysis["acao_recomendada"] != "registrar elogio sem ação operacional"
        if st.button(
            "Gerar e validar rascunho",
            icon=":material/fact_check:",
            disabled=not can_generate_draft,
            help="Indisponível quando o caso exige revisão humana ou não requer resposta operacional.",
        ):
            try:
                with st.spinner("Gerando, criticando e validando rascunho..."):
                    reflection = generate_safe_draft(
                        ticket["texto_cliente"], analysis, ticket["ticket_id"]
                    )
                    save_reflection(
                        ticket,
                        reflection.decision,
                        reflection.draft,
                        reflection.critiques,
                        reflection.attempts,
                        reflection.validation,
                    )
                st.rerun()
            except Exception as error:
                st.error(f"Não foi possível gerar o rascunho: {error}", icon=":material/error:")
        if st.button("Escalar para N2", icon=":material/escalator_warning:"):
            update_status(ticket, "Escalado para N2", "Escalonamento simulado")
            st.rerun()
        if st.button("Fechar ticket", icon=":material/task_alt:"):
            confirm_close(ticket["ticket_id"])

    reflection = ticket.get("reflexao")
    if reflection:
        st.subheader("Resultado do fluxo reflexivo")
        decision = reflection["decisao"]
        if decision == "aprovado":
            st.success("Rascunho aprovado pela crítica local.", icon=":material/check_circle:")
        elif decision == "revisado":
            st.info("Rascunho aprovado após uma revisão pela IA.", icon=":material/refresh:")
        elif decision == "reprovado":
            st.error(
                "Nenhum rascunho passou após três tentativas. Não há mensagem para exibir.",
                icon=":material/block:",
            )
        else:
            st.warning("Não há resposta automática para este caso; siga a decisão indicada.", icon=":material/person_alert:")
        with st.expander("Evidência da crítica", icon=":material/fact_check:"):
            st.write(f"**Decisão:** {decision}")
            st.write(f"**Tentativas de geração:** {reflection['tentativas']}")
            st.json(reflection["validacao"], expanded=False)
            for critique in reflection["critiques"]:
                st.caption(critique)

    if ticket["rascunho"]:
        st.subheader("Rascunho de resposta")
        response_key = f"reply_{ticket['ticket_id']}"
        if response_key not in st.session_state:
            st.session_state[response_key] = ticket["rascunho"]
        response_text = st.text_area("Resposta ao cliente", key=response_key, height=130)
        with st.container(horizontal=True):
            if st.button("Registrar resposta manual", icon=":material/reply:"):
                register_reply(ticket, response_text, automated=False)
                st.success("Resposta manual registrada na simulação.", icon=":material/check_circle:")
            if st.button("Simular resposta automática", icon=":material/smart_toy:"):
                confirm_automatic_reply(ticket["ticket_id"])

with st.expander("Histórico simulado", icon=":material/history:"):
    for entry in reversed(ticket["historico"]):
        st.write(f"**{entry.get('horario', 'Inicial')} · {entry['evento']}**")
        st.caption(f"{entry.get('responsavel', 'Não informado')} · {entry['detalhe']}")

with st.expander("Registro de execução", icon=":material/terminal:"):
    st.caption("Registro persistente desativado nesta versão para proteger as mensagens de demonstração.")
