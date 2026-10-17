# Obtainium Recomp Pack

Pack d'import [Obtainium](https://github.com/ImranR98/Obtainium) pour l'**AYN Thor** : ports de jeux **decomp / recomp** Android (arm64).
Complémentaire de l'[Obtainium Emulation Pack](https://github.com/RJNY/Obtainium-Emulation-Pack) (émulateurs, frontends) — aucun doublon.

## Installation

1. Sur la Thor, télécharge [`thor-pack.json`](https://raw.githubusercontent.com/kyure001/obtainium_recomp_pack/main/thor-pack.json).
2. Obtainium → **Import/Export** → **Obtainium Import** → sélectionne le fichier.
3. Pour mettre le pack à jour : réimporte le dernier `thor-pack.json` (les configs existantes sont mises à jour).

## Contenu

| Port | Jeu | Notes |
| --- | --- | --- |
| [Ship of Harkinian Dual Screen](https://github.com/chilhaps/Shipwright-Android-Dual-Screen) | Ocarina of Time | Second écran exploité, testé sur AYN Thor |
| [GoldenEye Recomp](https://github.com/jeffory/GoldenEye-Recomp) | GoldenEye 007 | GPU Adreno requis |
| [2 Ship 2 Harkinian](https://github.com/Waterdish/2ship2harkinian-Android) | Majora's Mask | |

Aucune ROM ni donnée de jeu n'est fournie : chaque port demande tes propres fichiers.

Le fichier est généré par `build.py` (`python3 build.py kyure001/obtainium_recomp_pack`).
