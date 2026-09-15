"""Estado temporário da demonstração, isolado por sessão Streamlit."""

from datetime import datetime

import streamlit as st

from core.audit import log_event
from core.data import load_demo_tickets


def initialize_state() -> None:
    st.session_state.setdefault("tickets", load_demo_tickets())
    st.session_state.setdefault("selected_ticket_id", None)
    st.session_state.setdefault("simulation_counter", 0)


def all_tickets() -> list[dict]:
    return st.session_state.tickets


def get_ticket(ticket_id: str | None) -> dict | None:
    return next((ticket for ticket in all_tickets() if ticket["ticket_id"] == ticket_id), None)


def select_ticket(ticket_id: str) -> None:
    st.session_state.selected_ticket_id = ticket_id
    log_event(ticket_id, "ticket_aberto", {"origem": "fila de atendimento"})


def _record(ticket: dict, event: str, detail: str, responsible: str) -> None:
    ticket["historico"].append(
        {
            "evento": event,
            "detalhe": detail,
            "responsavel": responsible,
            "horario": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
    )


def create_ticket(ticket_text: str, analysis: dict[str, str]) -> dict:
    st.session_state.simulation_counter += 1
    ticket = {
        "ticket_id": f"SIM-{st.session_state.simulation_counter:03d}",
        "texto_cliente": ticket_text,
        "tema_historico": "Não aplicável",
        "status": "Aberto",
        "origem": "Simulação do cliente",
        "analise": analysis,
        "rascunho": "",
        "reflexao": None,
        "historico": [],
    }
    _record(ticket, "Ticket recebido", "Ticket criado na simulação do cliente.", "Cliente")
    _record(ticket, "Classificação inicial", "Classificação gerada pela IA.", "IA")
    all_tickets().insert(0, ticket)
    select_ticket(ticket["ticket_id"])
    log_event(
        ticket["ticket_id"],
        "ticket_criado",
        {"origem": ticket["origem"], "classificacao": analysis},
    )
    return ticket


def save_analysis(ticket: dict, analysis: dict[str, str]) -> None:
    ticket["analise"] = analysis
    _record(ticket, "Ticket analisado", analysis["acao_recomendada"], "IA")
    log_event(ticket["ticket_id"], "ticket_analisado", {"classificacao": analysis})


def save_reflection(
    ticket: dict,
    decision: str,
    draft: str,
    critiques: list[str],
    attempts: int,
    validation: dict[str, str | bool],
) -> None:
    ticket["rascunho"] = draft
    ticket["reflexao"] = {
        "decisao": decision,
        "critiques": critiques,
        "tentativas": attempts,
        "validacao": validation,
    }
    detail = f"Decisão: {decision}. Tentativas de geração: {attempts}."
    if critiques:
        detail += f" Críticas: {' '.join(critiques)}"
    _record(ticket, "Fluxo reflexivo executado", detail, "IA e regra local")
    log_event(
        ticket["ticket_id"],
        "resultado_reflexivo_salvo",
        {
            "decisao": decision,
            "tentativas": attempts,
            "validacao": validation,
            "rascunho_exibido": bool(draft),
        },
    )


def update_status(ticket: dict, status: str, event: str, responsible: str = "Atendente") -> None:
    ticket["status"] = status
    _record(ticket, event, f"Status simulado: {status}.", responsible)
    log_event(
        ticket["ticket_id"],
        "status_atualizado",
        {"status": status, "evento": event, "responsavel": responsible},
    )


def register_reply(ticket: dict, reply: str, automated: bool) -> None:
    channel = "Resposta automática simulada" if automated else "Resposta manual simulada"
    responsible = "IA com confirmação do atendente" if automated else "Atendente"
    _record(ticket, channel, reply, responsible)
    update_status(ticket, "Em Análise", channel, responsible)
    log_event(
        ticket["ticket_id"],
        "resposta_registrada",
        {"automatica": automated, "responsavel": responsible, "resposta": reply},
    )
