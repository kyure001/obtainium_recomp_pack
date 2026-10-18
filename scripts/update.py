"""Vérifie chaque candidat (release avec .apk) et génère thor-pack.json + STATUS.md.
Usage : GITHUB_TOKEN=... python3 scripts/update.py owner/repo_du_pack"""
import json, os, re, sys, urllib.request

PACK_REPO = sys.argv[1]
TOKEN = os.environ.get("GITHUB_TOKEN", "")
RJNY = "https://raw.githubusercontent.com/RJNY/Obtainium-Emulation-Pack/main/obtainium-emulation-pack-latest.json"

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

cand = json.load(open("candidates.json"))["candidates"]
try:
    rjny_urls = {a["url"].rstrip("/").lower() for a in get(RJNY)["apps"]}
except Exception:
    rjny_urls = set()

apps, rows, taken = [], [], set()
for c in cand:
    url = f"https://github.com/{c['repo']}".lower()
    if url in rjny_urls:
        rows.append((c, "doublon", "déjà dans le pack RJNY")); continue
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
           "Xbox 360": 4283215696, "Mega Drive": 4280391411, "Mega-CD": 4282339765, "PC": 4288585374, "Pack": 4284513675,
           "Emulator": 4282153945}
used = []
for a in apps:
    for k in a["categories"]:
        if k not in used:
            used.append(k)
cats = {k: palette.get(k, 4288585374) for k in used}
json.dump({"apps": apps, "settings": {"categories": json.dumps(cats, ensure_ascii=False), "groupByCategory": True}},
          open("thor-pack.json", "w"), ensure_ascii=False, indent=2)

icon = {"ok": "✅", "sans-apk": "⛔", "erreur": "⚠️", "doublon": "♻️", "alternative": "↪️"}
with open("STATUS.md", "w") as f:
    f.write("# État des candidats\n\nGénéré automatiquement par le workflow. ✅ = dans le pack.\n\n| | Port | Console | Type | Dépôt | Détail |\n|---|---|---|---|---|---|\n")
    for c, s, d in rows:
        f.write(f"| {icon[s]} | {c['name']} | {c.get('console','')} | {c['cat']} | [{c['repo']}](https://github.com/{c['repo']}) | {d} |\n")
print(f"{len(apps) - 1} ports retenus sur {len(cand)} candidats")
