# 🥇 LME Sales Analysis 2026 — Streamlit Dashboard

## Structure du projet

```
your-repo/
├── app.py
├── requirements.txt
├── COPPER_ANALYSIS_04_2026_COF_KT_COF_MA.xlsx   ← votre fichier Excel
└── README.md
```

## 🚀 Déploiement sur Streamlit Cloud

### 1. Créer un repo GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Déployer sur Streamlit Cloud
1. Allez sur [share.streamlit.io](https://share.streamlit.io)
2. Cliquez **New app**
3. Sélectionnez votre repo / branch `main` / fichier `app.py`
4. Cliquez **Deploy**

### 3. Configurer l'URL GitHub dans le dashboard
Dans la sidebar du dashboard, activez **"Load from GitHub"** et collez l'URL raw de votre fichier Excel :

```
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/COPPER_ANALYSIS_04_2026_COF_KT_COF_MA.xlsx
```

> **Auto-refresh** : Les données se rechargent automatiquement toutes les heures (cache TTL=3600s).
> Pour forcer un rechargement immédiat, cliquez **Clear Cache** dans le menu Streamlit (⋮).

### 4. Mise à jour des données
Quand vous uploadez un nouveau fichier Excel sur GitHub :
```bash
git add COPPER_ANALYSIS_04_2026_COF_KT_COF_MA.xlsx
git commit -m "Update copper data - April 2026"
git push
```
Le dashboard Streamlit récupérera automatiquement les nouvelles données.

---

## 📊 Fonctionnalités du Dashboard

### Onglets de navigation
| Onglet | Contenu |
|--------|---------|
| 📈 LME Overview | Évolution LME All-In & Basic, comparaison par groupe clients |
| 🏭 Fixation Analysis | M-1, 3M-1, 3M-2 — tonnage, quantité, CA + tableau récapitulatif |
| 📊 KPI Summary | Tous les KPIs clés : CA, Qty, ES mm, Cross-Section, RC/CC Kg/km, AV €/km |
| 🔬 Deep Dive | Analyse par Family, RM, Spool Type, LME Projects, Cross Section |
| 📋 Raw Data | Tableau filtré téléchargeable + statistiques descriptives |

### Filtres disponibles
- 🏭 Entité (COFICAB Kenitra / COFICAB Maroc)
- 📅 Month
- 🧱 RM (PVC, PP, PE, COFDATA)
- 📦 FAMILY
- 🏢 Groups
- 📐 Cross Section mm
- 🔧 Fixation (M-1, 3M-1, 3M-2)
- 🪝 Spool Type (PRODUCED / PURCHASED)
- 🌐 LME Projects
- Sliders : LME SALES €/kg et BASIC LME €/kg

### KPIs calculés
- **CA €/km** → moyenne de UNIT PRICE €/km
- **Quantité** → somme QTY Km
- **Avg ES mm** → sous-total ES mm / sous-total Qty km
- **Avg Cross Section** → idem (ES mm / Qty km)
- **Avg Real Copper Kg/km** → sous-total RC Needs Kg / sous-total Qty km
- **Avg Commercial Copper Kg/km** → sous-total CC Needs Kg / sous-total Qty km
- **LME moyen** → moyenne LME SALES €/kg
- **Avg AV €/km** → sous-total AV INDEX / sous-total Qty km
- **Tonnage par Fixation** → RC Needs Kg / 1000 groupé par Fixation
