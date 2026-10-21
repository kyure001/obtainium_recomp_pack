"""Vérifie proposals.json (releases avec .apk) sans toucher au pack ; écrit PROPOSALS.md."""
import json, os, re, urllib.request

TOKEN = os.environ.get("GITHUB_TOKEN", "")

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "thor-pack"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

rows = []
for p in json.load(open("proposals.json"))["proposals"]:
    try:
        info = get(f"https://api.github.com/repos/{p['repo']}")
        rels = get(f"https://api.github.com/repos/{p['repo']}/releases?per_page=15")
    except Exception as e:
        rows.append((p, "⚠️", "", f"introuvable ({e})", "")); continue
    found = None
    for r in rels:
        if r.get("draft"):
            continue
        apks = [a for a in r.get("assets", []) if a["name"].lower().endswith(".apk")]
        if apks:
            found = (r, apks); break
    pushed = (info.get("pushed_at") or "")[:10]
    stars = info.get("stargazers_count", 0)
    if found:
        r, apks = found
        names = ", ".join(a["name"] for a in apks[:3]) + (" …" if len(apks) > 3 else "")
        pre = " (pré-version)" if r.get("prerelease") else ""
        rows.append((p, "✅", f"{r['tag_name']} — {r['published_at'][:10]}{pre}", names, f"★{stars}, actif {pushed}"))
    else:
        rows.append((p, "⛔", "", "aucune release avec APK", f"★{stars}, actif {pushed}"))

order = {"✅": 0, "⛔": 1, "⚠️": 2}
rows.sort(key=lambda x: (order[x[1]], x[0]["console"], x[0]["name"]))
with open("PROPOSALS.md", "w") as f:
    f.write("# Propositions à valider\n\nGénéré par le workflow `proposals.yml`. Rien ici n'est dans le pack.\n\n")
    f.write("| | Port | Console | Groupe | Dépôt | Dernière release | APK | Activité |\n|---|---|---|---|---|---|---|---|\n")
    for p, s, rel, apk, act in rows:
        f.write(f"| {s} | {p['name']} | {p['console']} | {p.get('group','')} | [{p['repo']}](https://github.com/{p['repo']}) | {rel} | {apk} | {act} |\n")
print(sum(1 for r in rows if r[1] == "✅"), "avec APK sur", len(rows))
