import json, sys
REPO = sys.argv[1] if len(sys.argv) > 1 else None  # "owner/name"

def gh_settings(about, app_name="", apk_filter="", prerelease=False, track_only=False):
    return {
        "includePrereleases": prerelease, "fallbackToOlderReleases": True,
        "filterReleaseTitlesByRegEx": "", "filterReleaseNotesByRegEx": "",
        "verifyLatestTag": False, "sortMethodChoice": "date",
        "useLatestAssetDateAsReleaseDate": False, "releaseTitleAsVersion": False,
        "github-creds": "", "GHReqPrefix": "", "trackOnly": track_only,
        "versionExtractionRegEx": "", "matchGroupToUse": "", "versionDetection": True,
        "releaseDateAsVersion": False, "useVersionCodeAsOSVersion": False,
        "apkFilterRegEx": apk_filter, "invertAPKFilter": False, "autoApkFilterByArch": True,
        "appName": app_name, "appAuthor": "", "shizukuPretendToBeGooglePlay": False,
        "allowInsecure": False, "exemptFromBackgroundUpdates": False,
        "skipUpdateNotifications": False, "about": about, "refreshBeforeDownload": False,
        "includeZips": False, "zippedApkFilterRegEx": "",
    }

def app(pid, url, author, name, about, apk_filter="", prerelease=False, track_only=False, cat="Ports"):
    return {
        "id": pid, "url": url, "author": author, "name": name,
        "otherAssetUrls": None, "apkUrls": None, "preferredApkIndex": 0,
        "additionalSettings": json.dumps(gh_settings(about, name, apk_filter, prerelease, track_only), separators=(",", ":")),
        "categories": [cat], "overrideSource": "GitHub",
        # IDs provisoires : Obtainium corrige l'ID au premier téléchargement
        "allowIdChange": True,
    }

apps = [
    app("thorpack.soh.dualscreen", "https://github.com/chilhaps/Shipwright-Android-Dual-Screen",
        "chilhaps", "Ship of Harkinian (Dual Screen)",
        "Ocarina of Time (decomp HarbourMasters), second écran exploité, testé sur AYN Thor. ROM fournie par l'utilisateur."),
    app("thorpack.goldeneye.recomp", "https://github.com/jeffory/GoldenEye-Recomp",
        "jeffory", "GoldenEye Recomp",
        "Recompilation de GoldenEye 007, GPU Adreno requis. Données de jeu fournies par l'utilisateur.",
        apk_filter="android-arm64\\.apk$"),
    app("thorpack.2ship.android", "https://github.com/Waterdish/2ship2harkinian-Android",
        "Waterdish", "2 Ship 2 Harkinian",
        "Majora's Mask (decomp HarbourMasters). ROM fournie par l'utilisateur."),
]
if REPO:
    owner = REPO.split("/")[0]
    apps.append(app("thorpack.self", f"https://github.com/{REPO}", owner, "Thor Obtainium Pack",
                    "Suivi des nouvelles versions du pack (réimporter le JSON).", track_only=True, cat="Pack"))

pack = {"apps": apps,
        "settings": {"categories": json.dumps({"Ports": 4294940672, "Pack": 4288585374}), "groupByCategory": True}}
json.dump(pack, open("thor-pack.json", "w"), ensure_ascii=False, indent=2)
print(f"{len(apps)} apps")
