# Projet Python Avancé

## Dépendances
Installez les packages requis :
```bash
pip install requests matplotlib pillow python-docx
```

## Utilisation

### Application desktop (Partie 1)
Pour lancer l'interface graphique :
```bash
python main.py
```

### Génération du rapport (Partie 2)
Pour exécuter le script de rapport :
```bash
python report.py
```
Le fichier est généré dans `rapport_output/`.

### Lancer les tests
Pour exécuter les tests unitaires :
```bash
python -m unittest tests/test_all.py -v
```
