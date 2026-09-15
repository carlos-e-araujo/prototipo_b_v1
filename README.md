# Módulo B, demonstração compartilhável

Aplicação Streamlit para demonstrar a triagem de tickets com IA. Esta distribuição é autônoma e usa exclusivamente dados sintéticos em `dados/atendimento_demo.csv`.

## Proteções da demonstração

- Não inclui nem lê bases em `dados/tratados/`.
- Não grava mensagens, rascunhos ou ações dos visitantes em disco.
- Ações de resposta, escalonamento e fechamento são somente simuladas e ficam restritas à sessão do navegador.
- A chave da API é lida de variável de ambiente e nunca deve ser versionada.

## Execução local

No diretório deste protótipo:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Preencha `ELO_AGENTS_API_KEY` no `.env` e execute:

```bash
.venv/bin/streamlit run app.py
```

## Deploy no Streamlit Community Cloud

1. Publique apenas esta pasta em um repositório privado no GitHub.
2. Crie o app em `share.streamlit.io`, com `app.py` como ponto de entrada.
3. Em **Advanced settings → Secrets**, informe:

```toml
ELO_AGENTS_API_KEY = "sua_chave"
ELO_AGENTS_MODEL = "openai/gemini-3-flash-preview"
```

4. Mantenha o app privado e convide os visualizadores pelo menu **Share**.

Cada classificação, geração ou validação consome a cota associada à chave Elo Agents configurada.
