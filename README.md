# 🏆 GYM LEPES — Desafio 90 Dias

Dashboard público do desafio fitness do GymLepes.

## Estrutura

```
├── index.html                        # Dashboard (GitHub Pages)
├── data/
│   └── participantes.json            # Dados das equipes (atualizado pelo bot)
├── scripts/
│   └── sync_planilha.py              # Sincroniza Google Sheets → JSON
└── .github/workflows/
    └── sync-planilha.yml             # GitHub Actions (roda a cada hora)
```

## Como funciona

1. O Google Sheets com os dados das equipes está publicado como CSV público.
2. O GitHub Actions roda `scripts/sync_planilha.py` **a cada hora** automaticamente.
3. O script baixa o CSV, converte para JSON e salva em `data/participantes.json`.
4. O dashboard (`index.html`) lê o JSON via `raw.githubusercontent.com` (CORS liberado).

## Dashboard

Hospedado em: **https://Cornellllio01.github.io/gymlepes-sync**

## Atualização manual

Acesse **Actions → Sincronizar Planilha GymLepes → Run workflow** para forçar uma atualização imediata.
