"""Vérifie chaque candidat (release avec .apk) et génère thor-pack.json + STATUS.md.
Le pack complète Recompa (recompa.app) : un candidat déjà dans le catalogue Recompa est exclu,
ainsi que tout son groupe (même jeu), sauf "keep": true. "recompa": true marque à la main
un jeu couvert par Recompa sous un autre dépôt.
Usage : GITHUB_TOKEN=... python3 scripts/update.py owner/repo_du_pack"""
import json, os, re, sys, urllib.request

PACK_REPO = sys.argv[1]
TOKEN = os.environ.get("GITHUB_TOKEN", "")
RJNY = "https://raw.githubusercontent.com/RJNY/Obtainium-Emulation-Pack/main/obtainium-emulation-pack-latest.json"
RECOMPA = "https://recompa.app/index.json"
RECOMPA_COPY = "recompa-repos.txt"  # dernière liste connue, utilisée si recompa.app ne répond pas

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "thor-pack"})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def settings(about, name, apk_filter="", prerelease=False, track_only=False):
    return {"includePrereleases": prerelease, "fallbackToOlderReleases": True,
            "filterReleaseTitlesByRegEx": "", "filterReleaseNotesByRegEx": "", "verifyLatestTag": False,
            "sortMethodChoice": "date", "useLatestAssetDateAsReleaseDate": False, "releaseTitleAsVersion": False,
            "github-creds": "", "GHReqPrefix": "", "trackOnly": track_only, "versionExtractionRegEx": "",
            "matchGroupToUse": "", "versionDetection": True, "releaseDateAsVersion": False,
            "useVersionCodeAsOSVersion": False, "apkFilterRegEx": apk_filter, "invertAPKFilter": False,
            "autoApkFilterByArch": True, "appName": name, "appAuthor": "", "shizukuPretendToBeGooglePlay": False,
            "allowInsecure": False, "exemptFromBackgroundUpdates": False, "skipUpdateNotifications": False,
            "about": about, "refreshBeforeDownload": False, "includeZips": False, "zippedApkFilterRegEx": ""}

def entry(c, prerelease, track_only=False):
    """'family' = 'Emulator' range l'appli chez les émulateurs dans ObtainX Thor ;
    'overrides' remplace des réglages Obtainium (ex. tag de release fixe)."""
    owner = c["repo"].split("/")[0]
    slug = re.sub(r"[^a-z0-9]+", ".", c["repo"].lower()).strip(".")
    return {"id": f"thorpack.{slug}", "url": f"https://github.com/{c['repo']}", "author": owner,
            "name": c["name"], "otherAssetUrls": None, "apkUrls": None, "preferredApkIndex": 0,
            "additionalSettings": json.dumps({**settings(f"[{c['cat']}] " + c["about"] + " Données de jeu à fournir.", c["name"],
                                                      c.get("filter", ""), prerelease, track_only), **c.get("overrides", {})},
                                             ensure_ascii=False),
            "categories": [c.get("family") or c.get("console", c["cat"])], "overrideSource": "GitHub", "allowIdChange": True}

def check(c):
    """Renvoie (statut, détail, prerelease)."""
    try:
        rels = get(f"https://api.github.com/repos/{c['repo']}/releases?per_page=15")
    except Exception as e:
        return "erreur", f"dépôt inaccessible ({e})", False
    flt = re.compile(c["filter"], re.I) if c.get("filter") else None
    for r in rels:
        if r.get("draft"):
            continue
        apks = [a["name"] for a in r.get("assets", []) if a["name"].lower().endswith(".apk")
                and (not flt or flt.search(a["name"]))]
        if apks:
            return "ok", f"{r['tag_name']} ({r['published_at'][:10]}) — {apks[0]}", bool(r.get("prerelease"))
    return "sans-apk", "aucune release avec APK", False

def recompa_repos():
    """Dépôts du catalogue Recompa (minuscules), anciens noms compris. Met à jour la copie locale."""
    try:
        idx = get(RECOMPA)
        repos = set()
        for p in idx["ports"]:
            for f in p.get("forks", []):
                repos.add(f["repo"].lower())
                owner = f["repo"].split("/")[0]
                olds = f.get("formerly") or []
                for old in [olds] if isinstance(olds, (str, dict)) else olds:
                    old = old if isinstance(old, str) else old.get("repo", "")
                    if old:
                        repos.add((old if "/" in old else f"{owner}/{old}").lower())
        if len(repos) > 50:  # garde-fou contre une réponse tronquée
            with open(RECOMPA_COPY, "w") as f:
                f.write(f"# Dépôts du catalogue Recompa ({RECOMPA}, généré le {idx.get('generated_at', '?')})\n")
                f.write("\n".join(sorted(repos)) + "\n")
            return repos, f"recompa.app ({len(repos)} dépôts)"
    except Exception as e:
        print(f"Recompa injoignable ({e}), copie locale utilisée")
    try:
        repos = {l.strip().lower() for l in open(RECOMPA_COPY) if l.strip() and not l.startswith("#")}
        return repos, f"copie locale {RECOMPA_COPY} ({len(repos)} dépôts)"
    except FileNotFoundError:
        return set(), "indisponible"

_canon = {}
def canonical(repo):
    """Nom actuel du dépôt (GitHub suit les renommages) ; le nom d'origine en cas d'erreur."""
    if repo not in _canon:
        try:
            _canon[repo] = get(f"https://api.github.com/repos/{repo}")["full_name"]
        except Exception:
            _canon[repo] = repo
    return _canon[repo]

cand = json.load(open("candidates.json"))["candidates"]
try:
    rjny_urls = {a["url"].rstrip("/").lower() for a in get(RJNY)["apps"]}
except Exception:
    rjny_urls = set()
rec, rec_src = recompa_repos()

def in_recompa(c):
    if c.get("recompa"):
        return "marqué à la main (même jeu dans Recompa)"
    if c["repo"].lower() in rec:
        return "dans Recompa"
    cur = canonical(c["repo"])
    if cur.lower() != c["repo"].lower() and cur.lower() in rec:
        return f"dans Recompa (dépôt renommé en {cur})"
    return ""

covered = {}  # groupe -> port du groupe présent dans Recompa
for c in cand:
    if c.get("group") and c["group"] not in covered and not c.get("keep") and in_recompa(c):
        covered[c["group"]] = c["name"]

apps, rows, taken = [], [], set()
for c in cand:
    url = f"https://github.com/{c['repo']}".lower()
    if url in rjny_urls:
        rows.append((c, "doublon", "déjà dans le pack RJNY")); continue
    if not c.get("keep"):
        why = in_recompa(c)
        if why:
            rows.append((c, "recompa", why)); continue
        if c.get("group") in covered:
            rows.append((c, "recompa", f"même jeu que {covered[c['group']]}, dans Recompa")); continue
    if c.get("group") and c["group"] in taken:
        rows.append((c, "alternative", "un autre port du même jeu est déjà retenu")); continue
    status, detail, pre = check(c)
    rows.append((c, status, detail))
    if status == "ok":
        apps.append(entry(c, pre))
        if c.get("group"):
            taken.add(c["group"])

apps.append(entry({"name": "Obtainium Recomp Pack", "repo": PACK_REPO, "cat": "Pack", "console": "Pack",
                   "about": "Suivi du pack : réimporter thor-pack.json quand il change."}, False, track_only=True))
palette = {"Nintendo 64": 4293467747, "GameCube": 4286336511, "Wii U": 4278228616, "Game Boy": 4287349578,
           "Xbox 360": 4283215696, "Mega Drive": 4280391411, "Mega-CD": 4282339765, "PC": 4288585374, "Pack": 4284513675, "Outil Thor": 4284513675, "Utilities": 4284513675,
           "Game Boy Advance": 4291460961, "PlayStation": 4283001054, "PlayStation 2": 4281219502,
           "Wii": 4290822336, "Xbox": 4280060446,
           "Emulator": 4282153945}
used = []
for a in apps:
    for k in a["categories"]:
        if k not in used:
            used.append(k)
cats = {k: palette.get(k, 4288585374) for k in used}
json.dump({"apps": apps, "settings": {"categories": json.dumps(cats, ensure_ascii=False), "groupByCategory": True}},
          open("thor-pack.json", "w"), ensure_ascii=False, indent=2)

icon = {"ok": "✅", "sans-apk": "⛔", "erreur": "⚠️", "doublon": "♻️", "alternative": "↪️", "recompa": "🅡"}
with open("STATUS.md", "w") as f:
    f.write("# État des candidats\n\nGénéré automatiquement par le workflow. ✅ = dans le pack. "
            "🅡 = exclu car disponible dans [Recompa](https://recompa.app) "
            f"(liste : {rec_src}). ♻️ = déjà dans le pack RJNY. ↪️ = autre port du même jeu retenu. "
            "⛔ = pas d'APK publié. ⚠️ = dépôt inaccessible.\n\n"
            "| | Port | Console | Type | Dépôt | Détail |\n|---|---|---|---|---|---|\n")
    for c, s, d in rows:
        f.write(f"| {icon[s]} | {c['name']} | {c.get('console','')} | {c['cat']} | [{c['repo']}](https://github.com/{c['repo']}) | {d} |\n")
print(f"{len(apps) - 1} ports retenus sur {len(cand)} candidats")
