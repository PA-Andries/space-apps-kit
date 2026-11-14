"""Rôle B (Données) : va chercher les données NASA et écrit les CSV de `data/`.

Ce dossier ne sert qu'à fabriquer les fichiers : le site ne l'importe jamais.
"""

import logging

# Hors du site, Streamlit signale à chaque import qu'il ne tourne pas : inutile dans un script.
logging.getLogger("streamlit").setLevel(logging.ERROR)
