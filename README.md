# Obtainium Recomp Pack

Pack d'import [Obtainium](https://github.com/ImranR98/Obtainium) pour l'**AYN Thor** : ports de jeux **decomp / recomp** (et quelques réimplémentations) Android arm64.
Complémentaire de l'[Obtainium Emulation Pack](https://github.com/RJNY/Obtainium-Emulation-Pack) (émulateurs, frontends) : les doublons sont exclus automatiquement.

## Installation

1. Sur la Thor, télécharge [`thor-pack.json`](https://raw.githubusercontent.com/kyure001/obtainium_recomp_pack/main/thor-pack.json).
2. Obtainium → **Import/Export** → **Obtainium Import** → sélectionne le fichier.
3. L'entrée « Obtainium Recomp Pack » te prévient quand le pack change : réimporte alors le dernier `thor-pack.json`.

## Contenu

Voir **[STATUS.md](STATUS.md)** : la liste à jour des ports retenus (✅) et de ceux écartés faute d'APK.

## Fonctionnement

- `candidates.json` : liste des ports candidats (à éditer pour en ajouter).
- `scripts/update.py` : vérifie chaque nuit que chaque dépôt publie un `.apk` en release, écarte les doublons du pack RJNY, et régénère `thor-pack.json` + `STATUS.md`.
- `.github/workflows/update.yml` : lance le script chaque nuit, à chaque modification des candidats, ou à la demande.

Aucune ROM ni donnée de jeu n'est fournie : chaque port demande tes propres fichiers.
