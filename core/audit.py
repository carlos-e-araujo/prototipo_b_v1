"""Auditoria desativada na versão compartilhável do protótipo."""

from pathlib import Path
from typing import Any


LOG_PATH = Path("Registro desativado para proteger mensagens de demonstração")


def log_event(ticket_id: str, event: str, details: dict[str, Any]) -> None:
    """Não persiste textos ou decisões de visitantes no ambiente compartilhado."""


def read_ticket_events(ticket_id: str, limit: int = 30) -> list[dict[str, Any]]:
    """Retorna vazio porque a distribuição não mantém log entre sessões."""
    return []
