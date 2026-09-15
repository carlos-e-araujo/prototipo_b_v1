"""Fluxo reflexivo: gerar, validar aderência e limitar tentativas da IA."""

from dataclasses import dataclass

from core.agent import draft_reply, revise_reply, validate_reply
from core.audit import log_event


MAX_ATTEMPTS = 3

BLOCKED_TERMS = (
    "</system",
    "<system",
    "system-reminder",
    "microsoft 365",
    "microsoft365",
    "outlook",
    "sharepoint",
    "project phoenix",
    "calendário",
    "calendar",
    "e-mail do meu chefe",
    "email from my boss",
    "csv",
    "docx",
    "/docx",
    "relatório",
    "report",
    "executive summary",
    "sales trends",
    "performance by region",
    "arquivo anexado",
    "attached file",
)

UNSUPPORTED_ACTION_TERMS = (
    "encaminhei",
    "encaminhamos",
    "verifiquei seu pedido",
    "já verifiquei",
    "enviei",
    "agendei",
)

HUMAN_ACTIONS = {
    "escalonar para atendimento humano",
    "revisão humana necessária",
}


@dataclass(frozen=True)
class ReflectionResult:
    decision: str
    draft: str
    critiques: list[str]
    attempts: int
    validation: dict[str, str | bool]


def critique_draft(draft: str) -> list[str]:
    """Aplica guardrails determinísticos antes da validação por IA."""
    normalized = draft.strip().lower()
    critiques: list[str] = []

    if not normalized:
        critiques.append("Rascunho vazio.")
    if len(draft.strip()) > 700:
        critiques.append("Rascunho excede o limite de 700 caracteres.")
    if "```" in draft or "{" in draft or "}" in draft:
        critiques.append("Rascunho contém marcação ou estrutura técnica indevida.")
    if any(term in normalized for term in BLOCKED_TERMS):
        critiques.append("Rascunho contém referência fora do contexto do atendimento.")
    if any(term in normalized for term in UNSUPPORTED_ACTION_TERMS):
        critiques.append("Rascunho afirma uma ação que o protótipo não executa.")
    return critiques


def _rejected_validation(justification: str) -> dict[str, str | bool]:
    return {"aprovado": False, "justificativa": justification}


def generate_safe_draft(
    ticket_text: str, analysis: dict[str, str], ticket_id: str = "desconhecido"
) -> ReflectionResult:
    """Gera até três rascunhos e só devolve texto aprovado pelo validador estruturado."""
    action = analysis["acao_recomendada"]
    log_event(ticket_id, "fluxo_reflexivo_iniciado", {"acao_recomendada": action})

    if action == "registrar elogio sem ação operacional":
        validation = _rejected_validation("Elogio não exige resposta operacional.")
        log_event(ticket_id, "fluxo_reflexivo_encerrado", {"decisao": "não aplicável", "validacao": validation})
        return ReflectionResult("não aplicável", "", [validation["justificativa"]], 0, validation)

    if action in HUMAN_ACTIONS or analysis["prioridade"] == "alta" or analysis["risco_de_churn"] == "alto":
        validation = _rejected_validation("A classificação requer tratamento humano prioritário.")
        log_event(ticket_id, "fluxo_reflexivo_encerrado", {"decisao": "revisão humana", "validacao": validation})
        return ReflectionResult("revisão humana", "", [validation["justificativa"]], 0, validation)

    candidate = ""
    critiques: list[str] = []
    last_validation = _rejected_validation("Nenhum rascunho foi validado.")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        if attempt == 1:
            candidate = draft_reply(ticket_text, action)
        else:
            candidate = revise_reply(ticket_text, action, candidate, critiques)

        log_event(ticket_id, "rascunho_gerado", {"tentativa": attempt, "rascunho": candidate})
        local_critiques = critique_draft(candidate)
        if local_critiques:
            last_validation = _rejected_validation("Reprovado pelas regras locais de segurança.")
            critiques.extend(local_critiques)
            log_event(
                ticket_id,
                "validacao_local_reprovada",
                {"tentativa": attempt, "criticas": local_critiques},
            )
            continue

        try:
            last_validation = validate_reply(ticket_text, analysis, candidate)
        except Exception as error:
            last_validation = _rejected_validation(
                f"Validação estruturada indisponível: {type(error).__name__}."
            )

        log_event(
            ticket_id,
            "validacao_estruturada",
            {"tentativa": attempt, "validacao": last_validation},
        )
        if last_validation["aprovado"]:
            decision = "aprovado" if attempt == 1 else "revisado"
            log_event(
                ticket_id,
                "fluxo_reflexivo_encerrado",
                {"decisao": decision, "tentativas": attempt, "validacao": last_validation},
            )
            return ReflectionResult(decision, candidate, critiques, attempt, last_validation)

        critiques.append(f"Validação de aderência reprovou: {last_validation['justificativa']}")

    final_validation = _rejected_validation(
        "O rascunho foi reprovado após três tentativas e não será exibido."
    )
    log_event(
        ticket_id,
        "fluxo_reflexivo_encerrado",
        {"decisao": "reprovado", "tentativas": MAX_ATTEMPTS, "validacao": final_validation},
    )
    return ReflectionResult("reprovado", "", critiques, MAX_ATTEMPTS, final_validation)
