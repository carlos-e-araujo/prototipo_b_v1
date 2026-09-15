"""Leitura dos tickets sintéticos incluídos na demonstração compartilhável."""

from pathlib import Path

import pandas as pd
import streamlit as st


SOURCE_PATH = Path(__file__).resolve().parents[1] / "dados" / "atendimento_demo.csv"


@st.cache_data
def load_demo_tickets() -> list[dict[str, str]]:
    """Carrega tickets sintéticos; a base distribuída não contém dados reais."""
    source = pd.read_csv(SOURCE_PATH, dtype=str)
    tickets: list[dict[str, str]] = []
    for _, row in source.iterrows():
        tickets.append(
            {
                "ticket_id": row["ticket_id"],
                "texto_cliente": row["texto_cliente"],
                "tema_historico": row["categoria_problema"],
                "status": row["status_atendimento"],
                "origem": "Base sintética de demonstração",
                "analise": None,
                "rascunho": "",
                "historico": [
                    {
                        "evento": "Ticket sintético carregado para demonstração",
                        "detalhe": "Origem: dados/atendimento_demo.csv",
                        "responsavel": "Base de demonstração",
                    }
                ],
            }
        )
    return tickets
