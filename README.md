# Obtainium Recomp Pack

An [Obtainium](https://github.com/ImranR98/Obtainium) import pack for the **AYN Thor** and other Android handhelds: arm64 Android builds of **decomp / recomp** game ports, a few engine reimplementations, and some dual-screen tools for the Thor.
It complements the [Obtainium Emulation Pack](https://github.com/RJNY/Obtainium-Emulation-Pack) (emulators, frontends): apps already in that pack are excluded automatically.

## Installation

### With ObtainX Thor (recommended)

[ObtainX Thor](https://github.com/kyure001/obtainXthor) subscribes to this pack out of the box and syncs it once a day: new ports appear on their own, and apps you remove do not come back.

### With Obtainium or ObtainX

1. On your device, download `thor-pack.json` from the [latest release](https://github.com/kyure001/obtainium_recomp_pack/releases/latest) (direct link: https://github.com/kyure001/obtainium_recomp_pack/releases/latest/download/thor-pack.json).
2. Obtainium → **Import/Export** → **Obtainium Import** → select the file.
3. The "Obtainium Recomp Pack" entry notifies you when the pack changes: re-import the latest `thor-pack.json` to get the new ports. Existing apps are updated, nothing is duplicated.

## What's inside

See **[STATUS.md](STATUS.md)** for the up-to-date list: ports included (✅), alternatives set aside, and candidates without an APK yet. Apps are grouped by original console.

## How it works

- `candidates.json`: the list of candidate ports. Edit it to add one.
- `scripts/update.py`: every night, checks that each repository publishes an `.apk` in its releases, skips duplicates of the RJNY pack, keeps a single port per game, and regenerates `thor-pack.json` and `STATUS.md`.
- `.github/workflows/update.yml`: runs the script every night, whenever the candidates change, or on demand, and publishes a new release when the pack changes.
- `proposals.json`, `scripts/check_proposals.py` and `PROPOSALS.md`: new projects being evaluated. They are checked the same way but are not part of the pack.

Suggestions are welcome: open an issue with the repository of a port that publishes an arm64 APK.

## Legal

No ROMs or game data are provided or linked. Every port requires your own legally obtained copy of the game. This pack only points to the official releases of each project.
