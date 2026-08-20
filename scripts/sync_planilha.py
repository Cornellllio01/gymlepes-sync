"""
Sincroniza a planilha Google Sheets do desafio GYM LEPES para um JSON
consumido pelo dashboard (via raw.githubusercontent.com, que tem CORS liberado).

Rodado automaticamente pelo GitHub Actions (.github/workflows/sync-planilha.yml).
"""
import csv
import json
import urllib.request
from datetime import datetime, timezone

SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vS58Ccnucbsw_e6Dhat1HRfmHC7tasbmclcJi8l5PvIfkTzfSkoiG-FLOXc0khBxa2a8Nmi0Vn9JlmF/"
    "pub?gid=733944384&single=true&output=csv"
)

# Mapeia o nome da equipe (como está na planilha) para id/cor usados no dashboard
TEAM_META = {
    "p.i.":     {"id": "pi",  "name": "P.I.",     "color": "#4ade80", "bg": "#0d2b1a"},
    "d.i.":     {"id": "di",  "name": "D.I.",     "color": "#f472b6", "bg": "#2b0d1a"},
    "g.e.":     {"id": "ge",  "name": "G.E.",     "color": "#60a5fa", "bg": "#0d1a2b"},
    "comunica": {"id": "com", "name": "Comunica", "color": "#fbbf24", "bg": "#2b220d"},
}

# Colunas do CSV (0-index): 0=vazia, 1=Nome, 2=Equipe, 3..15=13 semanas, ..., 25=PONTOS
COL_NOME = 1
COL_EQUIPE = 2
COL_SEMANA_INICIO = 3
COL_SEMANA_FIM = 15  # inclusive
COL_PONTOS = 25


def num(v):
    if v is None:
        return None
    v = v.strip().replace(",", ".")
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def main():
    req = urllib.request.Request(SHEET_CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")

    rows = list(csv.reader(raw.splitlines()))

    teams = {}
    for row in rows[1:]:
        if len(row) <= COL_PONTOS:
            row = row + [""] * (COL_PONTOS + 1 - len(row))

        nome = row[COL_NOME].strip()
        equipe_raw = row[COL_EQUIPE].strip()
        if not nome or not equipe_raw:
            continue

        weeks = [num(row[w]) for w in range(COL_SEMANA_INICIO, COL_SEMANA_FIM + 1)]
        pontos = num(row[COL_PONTOS]) or 0

        meta = TEAM_META.get(
            equipe_raw.lower(),
            {"id": "com", "name": equipe_raw, "color": "#999999", "bg": "#222222"},
        )
        t = teams.setdefault(meta["id"], {
            "id": meta["id"],
            "name": meta.get("name", equipe_raw),
            "color": meta["color"],
            "bg": meta["bg"],
            "members": [],
            "pontos_sum": 0.0,
            "count": 0,
        })
        t["members"].append({"name": nome, "weeks": weeks, "pontos": pontos})
        t["pontos_sum"] += pontos
        t["count"] += 1

    output_teams = []
    for t in teams.values():
        score = round(t["pontos_sum"] / t["count"], 1) if t["count"] else 0
        output_teams.append({
            "id": t["id"],
            "name": t["name"],
            "color": t["color"],
            "bg": t["bg"],
            "score": score,
            "members": t["members"],
        })

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "teams": output_teams,
    }

    with open("data/participantes.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total_pessoas = sum(t["count"] for t in teams.values())
    print(f"OK: {len(output_teams)} equipes, {total_pessoas} participantes sincronizados")


if __name__ == "__main__":
    main()
