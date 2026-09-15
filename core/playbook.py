"""Playbooks locais para transformar a classificação em próximo passo operacional."""

from dataclasses import dataclass


HUMAN_ACTIONS = {
    "escalonar para atendimento humano",
    "revisão humana necessária",
}


@dataclass(frozen=True)
class Playbook:
    title: str
    steps: tuple[str, ...]
    requires_human_review: bool
    note: str


def build_playbook(analysis: dict[str, str]) -> Playbook:
    """Retorna uma orientação local; não consulta nem simula sistemas externos."""
    action = analysis["acao_recomendada"]
    requires_human_review = (
        action in HUMAN_ACTIONS
        or analysis["prioridade"] == "alta"
        or analysis["risco_de_churn"] == "alto"
    )

    if action == "orientar status ou rastreio":
        return Playbook(
            title="Validar o andamento do pedido",
            steps=(
                "Consultar o rastreio somente em uma fonte integrada e verificável.",
                "Se não houver informação atualizada, escalar o caso para logística.",
                "Responder apenas com informações confirmadas ao cliente.",
            ),
            requires_human_review=requires_human_review,
            note="O protótipo não possui integração de rastreio e não informa localização ou prazo.",
        )
    if action == "coletar evidência":
        return Playbook(
            title="Completar as informações do caso",
            steps=(
                "Pedir ao cliente os detalhes e as evidências disponíveis.",
                "Registrar as informações recebidas no atendimento.",
                "Encaminhar para análise após receber evidências suficientes.",
            ),
            requires_human_review=requires_human_review,
            note="A coleta é uma solicitação ao cliente; nenhuma evidência é recebida automaticamente.",
        )
    if action == "encaminhar para fila especializada":
        return Playbook(
            title="Encaminhar para a equipe especializada",
            steps=(
                "Revisar a mensagem e os dados já disponíveis.",
                "Escalar para a fila responsável pelo tema.",
                "Registrar uma resposta somente após a orientação da equipe responsável.",
            ),
            requires_human_review=True,
            note="O encaminhamento é simulado e não aciona uma equipe externa.",
        )
    if action == "registrar elogio sem ação operacional":
        return Playbook(
            title="Registrar o elogio",
            steps=(
                "Registrar o feedback positivo para acompanhamento de experiência.",
                "Não gerar resposta automática operacional.",
            ),
            requires_human_review=False,
            note="O elogio não exige ação operacional neste fluxo demonstrativo.",
        )
    return Playbook(
        title="Revisar o caso antes de agir",
        steps=(
            "Ler a mensagem completa e validar a classificação sugerida.",
            "Definir a próxima ação manualmente ou escalar o atendimento.",
        ),
        requires_human_review=True,
        note="A recomendação exige decisão humana antes de qualquer resposta.",
    )
