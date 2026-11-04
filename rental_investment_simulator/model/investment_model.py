from typing import Dict, Any, List, Optional
import math


def safe_parse_float(value: Any) -> float:
    """
    Parse a value (string or number) to float safely.
    Returns 0.0 for invalid values.
    """
    try:
        if value is None or value == "":
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).replace(",", ".").replace(" ", "")
        return float(s)
    except Exception:
        return 0.0

class InvestmentModel:
    """
    Modèle financier d'un projet d'investissement immobilier.

    Cette classe contient toutes les données économiques et méthodes
    permettant de calculer rentabilité, cashflow, taux de couverture, etc.
    Elle ne dépend pas de la vue (UI) ni du presenter.

    Exemple:
        >>> model = InvestmentModel(price=200000, renovation=20000, surface_carrez=50,
        ...                         rent=1000, apport=40000, years=20, rate=0.035,
        ...                         monthly_income=3000, prix_moyen_m2=4500)
        >>> round(model.total_project)
        236000
    """

    VALORISATION_NON_CARREZ = 0.3  # pondération des surfaces hors Carrez

    def __init__(
        self,
        price: float = 1.0,
        furn: float = 0.0,
        other_fees: float = 0.0,
        renovation: float = 0.0,
        surface_carrez: float = 10.0,
        surface_non_validee: float = 0.0,
        taxe: float = 0.0,
        copro: float = 0.0,
        gestion_pct: float = 0.0,
        gli: float = 0.0,
        pno: float = 0.0,
        compta: float = 0.0,
        autres: float = 0.0,
        maintenance_pct: float = 0.0,
        vacancy_months: int = 0,
        rent: float = 500.0,
        apport: float = 0.0,
        years: int = 0,
        rate: float = 0.0,
        ins_rate: float = 0.0,
        monthly_income: float = 1.0,
        prix_moyen_m2: float = 200.0,
        type_of_property: str = "Ancien",
        finance_all: bool = True,
        extra_monthly_contribution: int = 0,
        dpe: str = "D"):
        """
        Initialise une instance du modèle d'investissement immobilier.

        Args:
            price (float, optional): Prix d'achat. Defaults to 0.0.
            furn (float, optional): Mobilier. Defaults to 0.0.
            other_fees (float, optional): Autres frais. Defaults to 0.0.
            renovation (float, optional): Travaux. Defaults to 0.0.
            surface_carrez (float, optional): Surface Carrez. Defaults to 0.0.
            surface_non_validee (float, optional): Surface hors Carrez. Defaults to 0.0.
            taxe (float, optional): Taxe foncière annuelle. Defaults to 0.0.
            copro (float, optional): Charges de copro. Defaults to 0.0.
            gestion_pct (float, optional): % gestion locative. Defaults to 0.0.
            gli (float, optional): Garantie loyers impayés (annuelle). Defaults to 0.0.
            pno (float, optional): Assurance PNO (annuelle). Defaults to 0.0.
            compta (float, optional): Frais compta (annuels). Defaults to 0.0.
            autres (float, optional): Autres charges annuelles. Defaults to 0.0.
            maintenance_pct (float, optional): % maintenance. Defaults to 0.0.
            vacancy_months (float, optional): Mois de vacance/an. Defaults to 0.0.
            rent (float, optional): Loyer mensuel brut. Defaults to 0.0.
            apport (float, optional): Apport personnel. Defaults to 0.0.
            years (float, optional): Durée prêt en années. Defaults to 0.0.
            rate (float, optional): Taux nominal du prêt. Defaults to 0.0.
            ins_rate (float, optional): Taux assurance du prêt. Defaults to 0.0.
            monthly_income (float, optional): Revenu mensuel investisseur. Defaults to 0.0.
            prix_moyen_m2 (float, optional): Prix moyen marché. Defaults to 0.0.
            type_of_property (str, optional): "Ancien" ou "Neuf". Defaults to "Ancien".
            finance_all (bool, optional): True si financement 100%. Defaults to True.   

        """
        numbers = {
            "price": price, "furn": furn, "other_fees": other_fees, "renovation": renovation,
            "surface_carrez": surface_carrez, "surface_non_validee": surface_non_validee,
            "taxe": taxe, "copro": copro, "gestion_pct": gestion_pct, "gli": gli, "pno": pno,
            "compta": compta, "autres": autres, "maintenance_pct": maintenance_pct,
            "vacancy_months": vacancy_months, "rent": rent, "apport": apport, "years": years,
            "rate": rate, "ins_rate": ins_rate, "monthly_income": monthly_income,
            "prix_moyen_m2": prix_moyen_m2,
        }
        integer_fields = {"vacancy_months", "years"}

        # --- Types ---
        for name, value in numbers.items():
            if name in integer_fields:
                if not isinstance(value, int):
                    raise TypeError(f"The {name} must be a integer not {type(value)}.")
            elif not isinstance(value, (int, float)):
                raise TypeError(f"The {name} must be a number not {type(value)}.")
        if not isinstance(type_of_property, str):
            raise TypeError(f"The type_of_property must be a str not {type(type_of_property)}.")
        if not isinstance(finance_all, bool):
            raise TypeError(f"The finance_all must be a bool not {type(finance_all)}.")

        # --- Valeurs finies ---
        for name, value in numbers.items():
            if math.isinf(value):
                raise ValueError(f"The {name} cannot be inf.")
            if math.isnan(value):
                raise ValueError(f"The {name} cannot be nan.")

        # --- Bornes ---
        for name in ("price", "surface_carrez", "rent", "monthly_income", "prix_moyen_m2"):
            if numbers[name] <= 0:
                raise ValueError(f"The {name} must be > 0.")
        for name in ("furn", "other_fees", "renovation", "surface_non_validee", "taxe", "copro",
                     "gestion_pct", "gli", "pno", "compta", "autres", "maintenance_pct",
                     "apport", "years"):
            if numbers[name] < 0:
                raise ValueError(f"The {name} cannot be negative.")
        if not 0 <= vacancy_months <= 12:
            raise ValueError("Vacancy months must be between 0 and 12.")
        for name in ("rate", "ins_rate"):
            if not 0 <= numbers[name] <= 1:
                raise ValueError(f"The {name} must be between 0 and 1 (decimal rate).")
        if type_of_property not in ("Ancien", "Neuf"):
            raise ValueError("Property type must be 'Ancien' or 'Neuf'.")

        # --- Affectations ---
        self.price = float(price)
        self.furn = float(furn)
        self.other_fees = float(other_fees)
        self.renovation = float(renovation)
        self.surface_carrez = float(surface_carrez)
        self.surface_non_validee = float(surface_non_validee)
        self.taxe = float(taxe)
        self.copro = float(copro)
        self.gestion_pct = float(gestion_pct)
        self.gli = float(gli)
        self.pno = float(pno)
        self.compta = float(compta)
        self.autres = float(autres)
        self.maintenance_pct = float(maintenance_pct)
        self.vacancy_months = float(vacancy_months)
        self.rent = float(rent)
        self.apport = float(apport)
        self.years = float(years)
        self.rate = float(rate)
        self.ins_rate = float(ins_rate)
        self.monthly_income = float(monthly_income)
        self.prix_moyen_m2 = float(prix_moyen_m2)
        self.type_of_property = str(type_of_property)
        self.finance_all = bool(finance_all)
        self.extra_monthly_contrib = int(extra_monthly_contribution)
        self.dpe = str(dpe)
        
        self.scoring_weights = {
            "cashflow": 30,
            "net_yield": 25,
            "ratio_marche": 15,
            "debt_ratio": 20,
            "ltv": 10
        }

    # -----------------------
    # Getters (calculs)
    # -----------------------


    @property
    def notary(self) -> float:
        """Frais de notaire en fonction du type de bien (8% ancien, 2.5% neuf)."""
        return self.price * (0.08 if self.type_of_property == "Ancien" else 0.025)

    @property
    def maintenance(self) -> float:
        """Montant annuel des frais de maintenance en fonction du prix du bien."""
        return self.price * self.maintenance_pct / 100.0

    @property
    def total_project(self) -> float:
        """Coût total du projet (prix + notaire + meubles + autres frais + rénovation)."""
        return self.price + self.notary + self.furn + self.other_fees + self.renovation

    @property
    def surface_totale_ponderee(self) -> float:
        """Surface pondérée incluant une valorisation des surfaces non Carrez (30%)."""
        return self.surface_carrez + self.VALORISATION_NON_CARREZ * self.surface_non_validee

    @property
    def price_carrez(self) -> float:
        """Prix au m² Carrez."""
        return self.total_project / self.surface_carrez if self.surface_carrez > 0 else 0.0

    @property
    def price_total_pondere(self) -> float:
        """Prix au m² pondéré (incluant surface non Carrez valorisée)."""
        return self.total_project / self.surface_totale_ponderee if self.surface_totale_ponderee > 0 else 0.0

    @property
    def ratio_marche(self) -> float:
        """Ratio du prix au m² pondéré comparé au marché (%)."""
        return (self.price_total_pondere / self.prix_moyen_m2 * 100) if self.prix_moyen_m2 > 0 else 0.0

    @property
    def loan_amount(self) -> float:
        """Montant du prêt bancaire (selon financement total ou prix seul)."""
        if self.finance_all:
            return max(0.0, self.total_project - self.apport)
        return max(0.0, self.price - self.apport)

    @property
    def n_months(self) -> int:
        """Durée du prêt en nombre total de mois."""
        return max(1, int(round(self.years * 12)))

    @property
    def monthly_payment_capital(self) -> float:
        """Mensualité du capital pour un prêt amortissable (hors assurance)."""
        monthly_rate = self.rate / 12.0
        if monthly_rate > 0:
            return (self.loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** (-self.n_months))
        return self.loan_amount / self.n_months if self.n_months > 0 else 0.0

    @property
    def monthly_insurance(self) -> float:
        """Mensualité de l'assurance emprunteur."""
        return self.loan_amount * self.ins_rate / 12.0

    @property
    def monthly_payment(self) -> float:
        """Mensualité totale (capital + assurance)."""
        return self.monthly_payment_capital + self.monthly_insurance

    @property
    def monthly_charges(self) -> float:
        """Charges mensuelles (taxe foncière, copropriété, gestion, GLI, PNO, compta, autres, maintenance).

        Remarques :
        - La GLI est prise ici comme un montant annuel fixe (divisé par 12), non réduit par la vacance.
        - La partie 'gestion' est calculée sur le loyer perçu (loyer * occupancy_rate).
        """
        taxe_m = self.taxe / 12.0
        copro_m = self.copro / 12.0
        # GLI considered as an annual fixed cost (not prorata by vacancy)
        gli_m = self.gli / 12.0
        pno_m = self.pno / 12.0
        compta_m = self.compta / 12.0
        autres_m = self.autres / 12.0
        maintenance_m = self.maintenance / 12.0
        gestion_m = (self.gestion_pct / 100.0) * (self.rent * self.occupancy_rate)
        return taxe_m + copro_m + gestion_m + gli_m + pno_m + compta_m + autres_m + maintenance_m

    @property
    def occupancy_rate(self) -> float:
        """Taux d'occupation annuel (1 - vacance locative / 12)."""
        return max(0.0, 1 - self.vacancy_months / 12.0)

    @property
    def effective_annual_rent(self) -> float:
        """Loyer annuel effectif tenant compte de la vacance locative."""
        return self.rent * 12 * self.occupancy_rate
    
    @property
    def break_even_rent(self) -> float:
        """Loyer mensuel minimum pour un cashflow nul.

        Résout : R × occupation × (1 - %gestion) - charges hors gestion - mensualité = 0.
        Retourne +inf si aucun loyer ne peut équilibrer (gestion ≥ 100 % ou vacance de 12 mois).
        """
        gestion_m = (self.gestion_pct / 100.0) * (self.rent * self.occupancy_rate)
        charges_hors_gestion = self.monthly_charges - gestion_m
        denominator = self.occupancy_rate * (1 - self.gestion_pct / 100.0)
        if denominator <= 0:
            return math.inf
        return (self.monthly_payment + charges_hors_gestion) / denominator

    @property
    def monthly_cashflow(self) -> float:
        """Cashflow mensuel net (loyer effectif - charges - mensualité + apport mensuel)."""
        return (
            self.effective_annual_rent / 12 
            - self.monthly_charges 
            - self.monthly_payment
            + self.extra_monthly_contrib
        )

    
    # --- Ratios financiers ---

    @property
    def gross_yield(self) -> float:
        """Rendement brut (%)."""
        return self.effective_annual_rent / self.total_project * 100 if self.total_project > 0 else 0.0

    @property
    def net_yield(self) -> float:
        """Rendement net (%)."""
        return ((self.effective_annual_rent - self.monthly_charges * 12) / self.total_project * 100) if self.total_project > 0 else 0.0

    @property
    def taux_couv(self) -> float:
        """Taux de couverture = (loyer effectif mensuel) / mensualité * 100."""
        monthly_rent = self.effective_annual_rent / 12.0
        return (monthly_rent / self.monthly_payment * 100) if self.monthly_payment > 0 else 0.0

    @property
    def ltv_price(self) -> float:
        """Loan-to-Value basé sur le prix du bien (%)."""
        return (self.loan_amount / self.price * 100) if self.price > 0 else 0.0

    @property
    def ltv_project(self) -> float:
        """Loan-to-Value basé sur le coût total du projet (%)."""
        return (self.loan_amount / self.total_project * 100) if self.total_project > 0 else 0.0

    @property
    def equity(self) -> float:
        """Fonds propres réellement investis = coût total du projet - montant emprunté.

        - Financement total (finance_all) : le prêt couvre frais, notaire, travaux et meubles,
          les fonds propres se limitent donc à l'apport.
        - Financement du prix seul : l'investisseur paie en plus notaire, frais, travaux et meubles.
        """
        return max(0.0, self.total_project - self.loan_amount)

    def principal_repaid_first_n_months(self, n=12) -> float:
        """
        Capital remboursé sur n mois, en tenant compte du prépaiement mensuel.
        """
        outstanding = self.loan_amount
        monthly_rate = self.rate / 12.0
        repaid = 0.0
    
        for _ in range(min(n, int(self.n_months))):
            interest = outstanding * monthly_rate
            principal = self.monthly_payment_capital - interest
            principal += self.extra_monthly_contrib   # prépaiement direct
            if principal <= 0:
                break
            repaid += principal
            outstanding -= principal
    
        return repaid


    @property
    def roe_cashflow(self) -> float:
        """
        ROE basé sur le cashflow réel (négatif si effort d'épargne important).
        """
        annual_cf = self.monthly_cashflow * 12
        return (annual_cf / self.equity * 100) if self.equity > 0 else 0.0
    
    @property
    def roe_patrimonial(self) -> float:
        """
        ROE intégrant le capital remboursé + cashflow net après prépaiement.
        """
        annual_capital_repaid = self.principal_repaid_first_n_months(12)
        annual_cf = self.monthly_cashflow * 12
        return ((annual_cf + annual_capital_repaid) / self.equity * 100) if self.equity > 0 else 0.0

    # -----------------------
    # Helpers
    # -----------------------

    def load_inputs(self, inputs: Dict[str, Any], type_of_property: str) -> None:
        """
        Charge un dictionnaire d'inputs dans les attributs du modèle.

        Args:
            inputs (Dict[str, Any]): Dictionnaire des valeurs d'entrée.
            type_of_property (str): Type de bien ("Ancien" ou "Neuf").
        """
        self.type_of_property = type_of_property
        for key, value in inputs.items():
            norm_key = key.replace(":", "").lower()
            if "prix d'achat" in norm_key:
                self.price = float(value)
            elif "meubles" in norm_key:
                self.furn = float(value)
            elif "autres frais" in norm_key:
                self.other_fees = float(value)
            elif "rénovation" in norm_key:
                self.renovation = float(value)
            elif "surface carrez" in norm_key:
                self.surface_carrez = float(value)
            elif "surface non" in norm_key:
                self.surface_non_validee = float(value)
            elif "taxe foncière" in norm_key:
                self.taxe = float(value)
            elif "charges copro" in norm_key:
                self.copro = float(value)
            elif "gestion" in norm_key:
                self.gestion_pct = float(value)
            elif "gli" in norm_key:
                self.gli = float(value)
            elif "pno" in norm_key:
                self.pno = float(value)
            elif "compta" in norm_key:
                self.compta = float(value)
            elif "autres charges" in norm_key:
                self.autres = float(value)
            elif "maintenance" in norm_key:
                self.maintenance_pct = float(value)
            elif "vacance" in norm_key:
                self.vacancy_months = float(value)
            elif "loyer" in norm_key:
                self.rent = float(value)
            elif "apport" in norm_key:
                self.apport = float(value)
            elif "revenu net" in norm_key:
                self.monthly_income = float(value)
            elif "durée" in norm_key:
                self.years = float(value)
            elif "taux d'intérêt" in norm_key:
                self.rate = float(value) / 100
            elif "assurance prêt" in norm_key:
                self.ins_rate = float(value) / 100
            elif "prix moyen" in norm_key:
                self.prix_moyen_m2 = float(value)
            elif "épargne mensuelle" in norm_key:
                self.extra_monthly_contrib = float(value)
            elif "dpe" in norm_key:
                self.dpe = str(value).upper()


    def validate(self) -> None:
        """Vérifie la cohérence des valeurs chargées (ex. via load_inputs).

        Lève ValueError avec la liste de tous les problèmes détectés.
        """
        errors: List[str] = []
        labels = {
            "price": "Prix d'achat", "furn": "Meubles", "other_fees": "Autres frais",
            "renovation": "Rénovation", "surface_carrez": "Surface Carrez",
            "surface_non_validee": "Surface non prise en compte", "taxe": "Taxe foncière",
            "copro": "Charges copropriété", "gestion_pct": "Gestion en agence", "gli": "GLI",
            "pno": "Assurance PNO", "compta": "Frais compta", "autres": "Autres charges",
            "maintenance_pct": "Maintenance", "vacancy_months": "Vacance locative",
            "rent": "Loyer mensuel", "apport": "Apport", "years": "Durée du prêt",
            "rate": "Taux d'intérêt", "ins_rate": "Assurance prêt",
            "monthly_income": "Revenu net mensuel", "prix_moyen_m2": "Prix moyen au m²",
            "extra_monthly_contrib": "Épargne mensuelle",
        }
        for attr, label in labels.items():
            if not math.isfinite(getattr(self, attr)):
                errors.append(f"{label} : valeur non finie.")
        if errors:
            raise ValueError("\n".join(errors))

        for attr in ("price", "surface_carrez", "rent", "monthly_income", "prix_moyen_m2"):
            if getattr(self, attr) <= 0:
                errors.append(f"{labels[attr]} doit être strictement positif.")
        for attr in ("furn", "other_fees", "renovation", "surface_non_validee", "taxe", "copro",
                     "gli", "pno", "compta", "autres", "maintenance_pct", "apport",
                     "extra_monthly_contrib"):
            if getattr(self, attr) < 0:
                errors.append(f"{labels[attr]} ne peut pas être négatif.")
        if not 0 <= self.gestion_pct <= 100:
            errors.append("Gestion en agence doit être entre 0 et 100 %.")
        if not 0 <= self.vacancy_months <= 12:
            errors.append("Vacance locative doit être entre 0 et 12 mois.")
        if self.years < 1:
            errors.append("Durée du prêt doit être d'au moins 1 an.")
        if not 0 <= self.rate <= 1:
            errors.append("Taux d'intérêt doit être entre 0 et 100 %.")
        if not 0 <= self.ins_rate <= 1:
            errors.append("Assurance prêt doit être entre 0 et 100 %.")
        if self.type_of_property not in ("Ancien", "Neuf"):
            errors.append("Type de bien doit être 'Ancien' ou 'Neuf'.")
        if self.dpe not in ("A", "B", "C", "D", "E", "F", "G"):
            errors.append("DPE doit être une lettre de A à G.")
        if errors:
            raise ValueError("\n".join(errors))

    def _evaluate_investment(self, adjusted_debt_ratio: float) -> tuple[str, str, str, Optional[float]]:
        """
        Évalue la viabilité de l’investissement avec un score pondéré et
        génère un diagnostic détaillé + conseils.
        Retourne (rec_text, rec_color, rec_details_text, proposed_price).
        """
        score = 0
        details: List[str] = []
        advice: List[str] = []
        proposed_price: Optional[float] = None

        # === Pondérations ===
        w = self.scoring_weights

        # Cashflow
        if self.monthly_cashflow > 100:
            score += w["cashflow"]; details.append(f"Cashflow >100€ (+{w['cashflow']})")
        elif self.monthly_cashflow >= 0:
            score += w["cashflow"] // 2; details.append(f"Cashflow neutre/faible (+{w['cashflow']//2})")
            advice.append("⚠️ Vérifier si le loyer peut être revalorisé ou les charges réduites.")
        else:
            details.append("Cashflow négatif : déficit mensuel (+0)")
            advice.append("❌ Le projet est déficitaire. Négociez le prix ou augmentez l’apport.")

        # Rendement net
        if self.net_yield >= 5:
            score += w["net_yield"]; details.append(f"Rendement net ≥5% (+{w['net_yield']})")
        elif self.net_yield >= 3:
            score += w["net_yield"] * 3 // 5; details.append(f"Rendement net 3–5% (+{w['net_yield']*3//5})")
            advice.append("⚠️ Rendement correct mais améliorable (travaux, gestion, loyer).")
        else:
            score += w["net_yield"] // 5; details.append(f"Rendement net <3% (+{w['net_yield']//5})")
            advice.append("❌ Rendement trop faible. Prix trop haut ou loyer trop bas.")

        # Ratio marché
        if self.ratio_marche <= 95:
            score += w["ratio_marche"]; details.append(f"Prix sous marché : opportunité (+{w['ratio_marche']})")
        elif self.ratio_marche <= 105:
            score += w["ratio_marche"] * 2 // 3; details.append(f"Prix au marché (+{w['ratio_marche']*2//3})")
        else:
            details.append("Prix au-dessus du marché (+0)")
            advice.append("❌ Bien surpayé. Négociez le prix ou comparez d’autres opportunités.")

        # Endettement
        if adjusted_debt_ratio <= 30:
            score += w["debt_ratio"]; details.append(f"Endettement ≤30% (+{w['debt_ratio']})")
        elif adjusted_debt_ratio <= 40:
            score += w["debt_ratio"] // 2; details.append(f"Endettement 30–40% (+{w['debt_ratio']//2})")
            advice.append("⚠️ Attention à la capacité d’emprunt, marge réduite.")
        else:
            details.append("Endettement >40% : risqué (+0)")
            advice.append("❌ Endettement trop élevé. Réduisez le montant du crédit ou augmentez l’apport.")

        # LTV
        if self.ltv_project <= 80:
            score += w["ltv"]; details.append(f"LTV ≤80% (+{w['ltv']})")
        elif self.ltv_project <= 90:
            score += w["ltv"] // 2; details.append(f"LTV 80–90% (+{w['ltv']//2})")
            advice.append("⚠️ Dépendance au crédit. Un apport supplémentaire réduirait le risque.")
        else:
            details.append("LTV >90% : risqué (+0)")
            advice.append("❌ Apport trop faible. Essayez d’investir plus de fonds propres.")

        # Synthèse globale
        total_max = sum(w.values())
        if score >= 0.75 * total_max:
            rec_text = "🟢 Investissement attractif"
            rec_color = "green"
        elif score >= 0.5 * total_max:
            rec_text = "🟡 Investissement moyen (à améliorer)"
            rec_color = "orange"
        else:
            rec_text = "🔴 Investissement risqué"
            rec_color = "red"

        rec_details_text = (
            f"Score final : {score}/{total_max}\n"
            + "\n".join(details)
            + "\n\n--- Conseils ---\n"
            + ("\n".join(advice) if advice else "✅ Aucun ajustement nécessaire.")
        )

        # --- Proposition de prix d'achat (argumentée) ---
        negotiation_argument = ""
        if self.ratio_marche > 105:
            target_ratio = 95
            proposed_price = self.price * (target_ratio / self.ratio_marche)
            negotiation_argument = (
                f"💡 Le bien est au-dessus du marché (ratio {self.ratio_marche:.1f} %). "
                f"Un prix cible de ~{proposed_price:,.0f} € serait cohérent avec un ratio de {target_ratio} %.\n"
                "Cet ajustement permettrait d’obtenir un cashflow proche de l’équilibre "
                "et un rendement net plus attractif (>4 %)."
            )
        elif self.ratio_marche > 100:
            proposed_price = self.price * (100 / self.ratio_marche)
            negotiation_argument = (
                f"💡 Le bien est légèrement au-dessus du marché ({self.ratio_marche:.1f} %). "
                f"Un prix ajusté à ~{proposed_price:,.0f} € le ramènerait au prix du marché."
            )
        else:
            negotiation_argument = (
                "✅ Le prix est déjà cohérent avec le marché. "
                "La négociation peut se concentrer sur la prise en charge de certains frais (ex: notaire ou copropriété)."
            )

        rec_details_text += "\n\n--- Proposition de prix ---\n" + negotiation_argument

        return rec_text, rec_color, rec_details_text, proposed_price
    
    # dans InvestmentModel (ajout en bas)
    def simulate_amortization(self, years: int = 20) -> List[Dict[str, float]]:
        """
        Simule année par année l'impact du prépaiement (extra_monthly_contrib).
        Retourne une liste de dictionnaires : année, capital restant dû, cashflow cumulé, patrimoine net.
        """
        outstanding = self.loan_amount
        monthly_rate = self.rate / 12.0
        results = []
    
        cum_cashflow = 0.0
        cum_principal = 0.0
    
        for year in range(1, years + 1):
            annual_cf = 0.0
            annual_principal = 0.0
    
            for _ in range(12):
                if outstanding <= 0:
                    break
    
                interest = outstanding * monthly_rate
                principal = self.monthly_payment_capital - interest + self.extra_monthly_contrib
    
                # Cashflow net (loyer - charges - mensualité - effort d’épargne)
                monthly_cf = (self.effective_annual_rent / 12
                              - self.monthly_charges
                              - self.monthly_payment
                              - self.extra_monthly_contrib)
    
                annual_cf += monthly_cf
                annual_principal += principal
                outstanding -= principal
    
                if outstanding < 0:
                    outstanding = 0
    
            cum_cashflow += annual_cf
            cum_principal += annual_principal
            patrimoine = cum_cashflow + cum_principal
    
            results.append({
                "Année": year,
                "Capital restant dû": outstanding,
                "Cashflow annuel": annual_cf,
                "Cashflow cumulé": cum_cashflow,
                "Capital remboursé cumulé": cum_principal,
                "Patrimoine net": patrimoine,
            })
    
            if outstanding <= 0:
                break
    
        return results


        
    def compute(self, inputs: dict) -> dict:
        """
        Calcule toutes les métriques financières et retourne un dictionnaire
        avec uniquement des valeurs numériques et quelques données pour la vue.
        """
        # Charger les inputs dans le modèle
        prop_type = inputs.get("Type de bien", "Ancien")
        self.load_inputs(inputs, prop_type)
        self.validate()
    
        # === Core metrics ===
        total_loan_cost = self.monthly_payment * self.n_months
        adjusted_debt_ratio = self.monthly_payment / (self.monthly_income or 1) * 100
    
        break_even_rent = self.break_even_rent
    
        # Pie data
        pie_data = {
            "Mensualité prêt": self.monthly_payment,
            "Taxe foncière": self.taxe/12,
            "Charges copro": self.copro/12,
            "Gestion agence": self.gestion_pct / 100.0 * self.rent * self.occupancy_rate,
            "GLI": self.gli / 12,
            "Assurance PNO": self.pno/12,
            "Frais compta": self.compta/12,
            "Autres": self.autres/12,
            "Maintenance": self.maintenance/12,
            "Cashflow": max(0.0, self.monthly_cashflow)
        }
    
        # Payback
        cumulative_cashflow: List[float] = []
        total = -self.equity
        payback_year: Optional[int] = None
        years_int = int(self.years) if self.years >= 1 else 1
        annual_cf = self.monthly_cashflow * 12
        for y in range(1, years_int + 1):
            total += annual_cf
            cumulative_cashflow.append(total)
            if total >= 0 and payback_year is None:
                payback_year = y
    
        # === Recommandation factorisée ===
        rec_text, rec_color, rec_details_text, proposed_price = self._evaluate_investment(adjusted_debt_ratio)
    
        # === Résultats finaux ===
        return {
            "total_project": self.total_project,
            "notary": self.notary,
            "price_carrez": self.price_carrez,
            "price_total_pondere": self.price_total_pondere,
            "monthly_cashflow": self.monthly_cashflow,
            "gross_yield": self.gross_yield,
            "net_yield": self.net_yield,
            "ltv": self.ltv_project,
            "roe": self.roe_cashflow,
            "monthly_payment": self.monthly_payment,
            "monthly_charges": self.monthly_charges,
            "annual_rent": self.effective_annual_rent,
            "maintenance": self.maintenance,
            "ratio_marche": self.ratio_marche,
            "loan_ratio": total_loan_cost / self.total_project * 100,
            "loan_amount": self.loan_amount,
            "break_even_rent": break_even_rent,
            "equity": self.equity,
            "price_per_m2": self.price_carrez,
            "total_loan_cost": total_loan_cost,
            "credit_cost": total_loan_cost - self.loan_amount,
            "adjusted_debt_ratio": adjusted_debt_ratio,
            "pie_data": pie_data,
            "cumulative_cashflow": cumulative_cashflow,
            "payback_year": payback_year,
            "rec_text": rec_text,
            "rec_color": rec_color,
            "rec_details_text": rec_details_text,
            "proposed_price": proposed_price,  # ✅ ajouté
            "cashflow": self.monthly_cashflow,
            "taux_couv": self.taux_couv,
            "debt_ratio": adjusted_debt_ratio,
        }
