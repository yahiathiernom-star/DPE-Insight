# DPE-Insight

Analyse exploratoire des diagnostics de performance énergétique des logements existants en Seine-Saint-Denis (93), à partir des données ouvertes de l’ADEME.

## Récupérer les données

Les données brutes ne sont pas versionnées dans Git. Chaque membre de l’équipe récupère sa copie localement en exécutant le même script ; l’extraction est filtrée sur le code départemental BAN `93` et limitée aux champs utiles au cadrage (dates, étiquettes énergie et climat, consommation, émissions, surface, construction, type de bâtiment, chauffage et commune). Les adresses ne sont pas téléchargées.

Après avoir récupéré la branche du projet, lancer (connexion Internet requise) :

```bash
python3 src/download.py
```

Pour vérifier rapidement l’accès à l’API avec un petit échantillon :

```bash
python3 src/download.py --limit 100
```

Le script enregistre les fichiers localement dans `data/raw/` et crée un manifest avec la date, le nombre de lignes et l’empreinte du fichier. La source ADEME est actualisée chaque semaine ; l’équipe doit donc éviter de relancer les téléchargements à des dates différentes une fois l’analyse commencée, ou se mettre d’accord sur une copie commune hors Git.

## Lancer le projet

Environnement prévu : Python 3.11 ou supérieur. Les analyses et le tableau de bord seront ajoutés dans les étapes suivantes.

## Précautions

Les lignes sont des diagnostics enregistrés, pas nécessairement des logements uniques. La base ADEME ne représente pas l’ensemble du parc immobilier. Les résultats décrivent les diagnostics exploitables du périmètre et ne démontrent pas de causalité.
