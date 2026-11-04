# Simulateur d'investissement locatif

Application de bureau (CustomTkinter + Matplotlib) qui calcule la rentabilité d'un investissement locatif : cashflow, rendements brut et net, loyer seuil de rentabilité, LTV, taux d'endettement, délai de retour sur investissement, et une recommandation sous forme de score.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # ou requirements.txt sans les outils de test
```

## Lancer l'application

```bash
python main.py
```

Le bouton **Calculer** génère aussi, dans le dossier courant :

- `rapport_investissement.txt` : le dossier d'investissement (destiné à la banque) ;
- `charges_pie.png` : la répartition du loyer (mensualité, charges, cashflow) ;
- `payback_period.png` : le cashflow cumulé année par année.

## Tests

```bash
pytest
```

## Architecture (MVP)

| Dossier | Rôle |
|---|---|
| `model/` | Calculs financiers (`InvestmentModel`). Aucune dépendance à l'interface. |
| `view/` | Interface CustomTkinter et graphiques (`InvestmentView`). |
| `presenter/` | Lit les saisies, appelle le modèle, met à jour la vue, génère le rapport. |
| `tests/` | Tests pytest et hypothesis ; `conftest.py` fournit une `FakeView` pour tester le presenter sans Tk. |

## Hypothèses de calcul à connaître

- Frais de notaire forfaitaires : 8 % (ancien) / 2,5 % (neuf).
- Surfaces hors Carrez valorisées à 30 %.
- Taux d'endettement simplifié : mensualité / revenu net (sans les loyers ni les autres crédits).
- Le ratio marché compare le prix d'achat au m² pondéré (hors notaire, travaux et meubles) au prix moyen du marché.
