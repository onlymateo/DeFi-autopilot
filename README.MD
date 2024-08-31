v1.0
# DeFi autopilot
## Description
Ce projet est un algorythme de sniper en Python utilisant l'API de DEXTools pour récupérer des tokens (cryptomonnaies) et leurs adresses, et utilisant IsRug pour noter leur fiabilité et éviter les anarques. Le projet est réalisé en collaboration avec @rayananas.



## Fonctionnalités
- Récupération des tokens : Utilisation de l'API de DEXTools pour récupérer des informations sur les tokens.
- Vérification anti-scam : Utilisation de IsRug pour vérifier la légitimité des tokens.
- Multitraitement : Optimisation des performances grâce à l'utilisation du module multiprocessing.
## Prérequis
Python 3.x
Les modules Python suivants :
- os
- sys
- time
- select
- termios
- requests
- fake_useragent
- multiprocessing

## Installation
Cloner le dépôt :


```bash
    git clone https://github.com/onlymateo/DeFi-autopilot.git
    cd DeFi-autopilot
```
## Installer les dépendances :

```bash
    pip install requests fake_useragent
```

## Utilisation
Pour lancer le bot en mode test, utilisez la commande suivante :

```bash
    defi-autopilot.py ethereum dry-run
```

## TODO
v1.1
