from typing import Dict, Tuple, Any, List, Optional
import math
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


VALORISATION_NON_CARREZ = 0.3  # pondération surface non valorisée

def parse_float_from_entry(entry_widget) -> float:
    """
    Safely parse a float from a CTkEntry-like widget.
    Returns 0.0 on empty or invalid input.
    """
    try:
        s = entry_widget.get()
        if s is None or s == "":
            return 0.0
        s = str(s).replace(",", ".").replace(" ", "")
        return float(s)
    except Exception:
        return 0.0


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

def color_gradient(value: float,
                   thresholds: Tuple[float, float, float] = (5, 10, 20),
                   colors: Tuple[str, str, str] = ("red", "orange", "green")) -> str:
    """
    Retourne une couleur en fonction d'une valeur numérique et de seuils.

    Args:
        value (int): La valeur numérique à évaluer.
        thresholds (tuple): Seuils (bas, moyen, haut).
        colors (tuple): Couleurs correspondantes.

    Returns:
        str: Couleur choisie.
    """
    low, medium, high = thresholds
    if value < low:
        return colors[0]
    if value < medium:
        return colors[1]
    return colors[2]

class InvestmentModel:
    """
    Modèle financier d'un projet d'investissement immobilier.

    Cette classe contient toutes les données économiques et méthodes
    permettant de calculer rentabilité, cashflow, taux de couverture, etc.
    Elle ne dépend pas de la vue (UI) ni du presenter.

    Exemple concret:
        >>> model = InvestmentModel(
        ...     "Prix d'achat": 200000,
        ...     "Meubles": 10000,
        ...     "Rénovation": 20000,
        ...     "Surface Carrez": 50,
        ...     "Surface non Carrez": 10,
        ...     "Taxe foncière": 1200,
        ...     "Charges copro": 600,
        ...     "Gestion": 7,
        ...     "Loyer": 1000,
        ...     "Apport": 40000,
        ...     "Durée": 20,
        ...     "Taux d'intérêt": 1.5,
        ...     "Assurance prêt": 0.3,
        ...     "Prix moyen": 4500
        ... )
        >>> model.load_inputs(inputs, type_of_property="Ancien")
        >>> round(model.gross_yield, 2)
        5.23
        >>> round(model.monthly_cashflow, 2)
        234.56
    """

    VALORISATION_NON_CARREZ = 0.3

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
        finance_all: bool = True):
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
        if not isinstance(price, (int, float)):
            raise TypeError(f"The price must be a number not {type(price)}.")
        if not isinstance(furn, (int, float)):
            raise TypeError(f"The furn must be a number not {type(furn)}.")
        if not isinstance(other_fees, (int, float)):
            raise TypeError(f"The other_fees must be a number not {type(other_fees)}.")
        if not isinstance(renovation, (int, float)):
            raise TypeError(f"The renovation must be a number not {type(renovation)}.")
        if not isinstance(surface_carrez, (int, float)):
            raise TypeError(f"The surface_carrez must be a number not {type(surface_carrez)}.")
        if not isinstance(surface_non_validee, (int, float)):
            raise TypeError(f"The surface_non_validee must be a number not {type(surface_non_validee)}.")
        if not isinstance(taxe, (int, float)):
            raise TypeError(f"The taxe must be a number not {type(taxe)}.")
        if not isinstance(copro, (int, float)):
            raise TypeError(f"The copro must be a number not {type(copro)}.")
        if not isinstance(gestion_pct, (int, float)):
            raise TypeError(f"The gestion_pct must be a number not {type(gestion_pct)}.")
        if not isinstance(gli, (int, float)):
            raise TypeError(f"The gli must be a number not {type(gli)}.")
        if not isinstance(pno, (int, float)):
            raise TypeError(f"The pno must be a number not {type(pno)}.")
        if not isinstance(compta, (int, float)):
            raise TypeError(f"The compta must be a number not {type(compta)}.")
        if not isinstance(autres, (int, float)):
            raise TypeError(f"The autres must be a number not {type(autres)}.")
        if not isinstance(maintenance_pct, (int, float)):
            raise TypeError(f"The maintenance_pct must be a number not {type(maintenance_pct)}.")
        if not isinstance(vacancy_months, int):
            raise TypeError(f"The vacancy_months must be a integer not {type(vacancy_months)}.")
        if not isinstance(rent, (int, float)):
            raise TypeError(f"The rent must be a number not {type(rent)}.")
        if not isinstance(apport, (int, float)):
            raise TypeError(f"The apport must be a number not {type(apport)}.")
        if not isinstance(years, int):
            raise TypeError(f"The years must be a integer not {type(years)}.")
        if not isinstance(rate, (int, float)):
            raise TypeError(f"The rate must be a number not {type(rate)}.")
        if not isinstance(ins_rate, (int, float)):
            raise TypeError(f"The ins_rate must be a number not {type(ins_rate)}.")
        if not isinstance(monthly_income, (int, float)):
            raise TypeError(f"The monthly_income must be a number not {type(monthly_income)}.")
        if not isinstance(prix_moyen_m2, (int, float)):
            raise TypeError(f"The prix_moyen_m2 must be a number not {type(prix_moyen_m2)}.")
        if not isinstance(type_of_property, str):
            raise TypeError(f"The type_of_property must be a str not {type(type_of_property)}.")
        if not isinstance(finance_all, bool):
            raise TypeError(f"The finance_all must be a bool not {type(finance_all)}.")


        if math.isinf(price):
            raise ValueError("The price cannot be inf.")
        elif math.isinf(furn):
            raise ValueError("The furn cannot be inf.")
        elif math.isinf(other_fees):
            raise ValueError("The other_fees cannot be inf.")
        elif math.isinf(renovation):
            raise ValueError("The renovation cannot be inf.")
        elif math.isinf(surface_carrez):
            raise ValueError("The surface_carrez cannot be inf.")
        elif math.isinf(surface_non_validee):
            raise ValueError("The surface_non_validee cannot be inf.")
        elif math.isinf(taxe):
            raise ValueError("The taxe cannot be inf.")
        elif math.isinf(copro):
            raise ValueError("The copro cannot be inf.")
        elif math.isinf(gestion_pct):
            raise ValueError("The gestion_pct cannot be inf.")
        elif math.isinf(gli):
            raise ValueError("The gli cannot be inf.")
        elif math.isinf(pno):
            raise ValueError("The pno cannot be inf.")
        elif math.isinf(compta):
            raise ValueError("The compta cannot be inf.")
        elif math.isinf(autres):
            raise ValueError("The autres cannot be inf.")
        elif math.isinf(maintenance_pct):
            raise ValueError("The maintenance_pct cannot be inf.")
        elif math.isinf(vacancy_months):
            raise ValueError("The vacancy_months cannot be inf.")
        elif math.isinf(rent):
            raise ValueError("The rent cannot be inf.")
        elif math.isinf(apport):
            raise ValueError("The apport cannot be inf.")
        elif math.isinf(years):
            raise ValueError("The years cannot be inf.")
        elif math.isinf(rate):
            raise ValueError("The rate cannot be inf.")
        elif math.isinf(ins_rate):
            raise ValueError("The ins_rate cannot be inf.")
        elif math.isinf(monthly_income):
            raise ValueError("The monthly_income cannot be inf.")
        elif math.isinf(prix_moyen_m2):
            raise ValueError("The prix_moyen_m2 cannot be inf.")
            
        if math.isnan(price):
            raise ValueError("The price cannot be nan.")
        elif math.isnan(furn):
            raise ValueError("The furn cannot be nan.")
        elif math.isnan(other_fees):
            raise ValueError("The other_fees cannot be nan.")
        elif math.isnan(renovation):
            raise ValueError("The renovation cannot be nan.")
        elif math.isnan(surface_carrez):
            raise ValueError("The surface_carrez cannot be nan.")
        elif math.isnan(surface_non_validee):
            raise ValueError("The surface_non_validee cannot be nan.")
        elif math.isnan(taxe):
            raise ValueError("The taxe cannot be nan.")
        elif math.isnan(copro):
            raise ValueError("The copro cannot be nan.")
        elif math.isnan(gestion_pct):
            raise ValueError("The gestion_pct cannot be nan.")
        elif math.isnan(gli):
            raise ValueError("The gli cannot be nan.")
        elif math.isnan(pno):
            raise ValueError("The pno cannot be nan.")
        elif math.isnan(compta):
            raise ValueError("The compta cannot be nan.")
        elif math.isnan(autres):
            raise ValueError("The autres cannot be nan.")
        elif math.isnan(maintenance_pct):
            raise ValueError("The maintenance_pct cannot be nan.")
        elif math.isnan(vacancy_months):
            raise ValueError("The vacancy_months cannot be nan.")
        elif math.isnan(rent):
            raise ValueError("The rent cannot be nan.")
        elif math.isnan(apport):
            raise ValueError("The apport cannot be nan.")
        elif math.isnan(years):
            raise ValueError("The years cannot be nan.")
        elif math.isnan(rate):
            raise ValueError("The rate cannot be nan.")
        elif math.isnan(ins_rate):
            raise ValueError("The ins_rate cannot be nan.")
        elif math.isnan(monthly_income):
            raise ValueError("The monthly_income cannot be nan.")
        elif math.isnan(prix_moyen_m2):
            raise ValueError("The prix_moyen_m2 cannot be nan.")
        # elif math.isnan(type_of_property):
        #     raise ValueError("The type_of_property cannot be nan.")
        elif math.isnan(finance_all):
            raise ValueError("The finance_all cannot be nan.")

        if price <= 0:
            raise ValueError("The price cannot be <= 0.")
        elif furn < 0:
            raise ValueError("Furnishings (furn) cannot be negative.")
        elif other_fees < 0:
            raise ValueError("Other fees cannot be negative.")
        elif renovation < 0:
            raise ValueError("Renovation costs cannot be negative.")
        elif surface_carrez <= 0:
            raise ValueError("Surface Carrez must be > 0.")
        elif surface_non_validee < 0:
            raise ValueError("Non-Carrez surface cannot be negative.")
        elif taxe < 0:
            raise ValueError("Property tax cannot be negative.")
        elif copro < 0:
            raise ValueError("Copropriété charges cannot be negative.")
        elif gestion_pct < 0:
            raise ValueError("Gestion percentage cannot be negative.")
        elif gli < 0:
            raise ValueError("GLI (insurance) cannot be negative.")
        elif pno < 0:
            raise ValueError("PNO (insurance) cannot be negative.")
        elif compta < 0:
            raise ValueError("Accounting fees cannot be negative.")
        elif autres < 0:
            raise ValueError("Other annual charges cannot be negative.")
        elif maintenance_pct < 0:
            raise ValueError("Maintenance percentage cannot be negative.")
        elif vacancy_months < 0 or vacancy_months > 12:
            raise ValueError("Vacancy months must be between 0 and 12.")
        elif rent <= 0:
            raise ValueError("Rent must be > 0.")
        elif apport < 0:
            raise ValueError("Downpayment (apport) cannot be negative.")
        elif years < 0:
            raise ValueError("Loan duration (years) cannot be negative.")
        elif not 0  <= rate <= 1:
            raise ValueError("Interest rate cannot be negative or below 1.")
        elif not 0  <= ins_rate <= 1:
            raise ValueError("Insurance rate cannot be negative.")
        elif monthly_income <= 0:
            raise ValueError("Monthly income must be > 0.")
        elif prix_moyen_m2 <= 0:
            raise ValueError("Market average price per m² must be > 0.")
        elif type_of_property not in ["Ancien", "Neuf"]:
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
    def monthly_cashflow(self) -> float:
        """Cashflow mensuel net (loyer effectif - charges - mensualité)."""
        return self.effective_annual_rent / 12 - self.monthly_charges - self.monthly_payment

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
        """Fonds propres investis (apport + frais + notaire + rénovation + meubles)."""
        return self.apport + self.renovation + self.furn + self.other_fees + self.notary

    @property
    def roe_cashflow(self) -> float:
        """ROE cashflow (%) : Rentabilité des fonds propres basée sur le cashflow net annuel."""
        return ((self.effective_annual_rent - self.monthly_charges * 12 - self.monthly_payment * 12) / self.equity * 100) if self.equity > 0 else 0.0

    def principal_repaid_first_n_months(self, n=12) -> float:
        """Calcul exact du capital remboursé sur les n premiers mois via le plan d'amortissement."""
        outstanding = self.loan_amount
        monthly_rate = self.rate / 12.0
        payment = self.monthly_payment_capital
        repaid = 0.0
        for _ in range(min(n, int(self.n_months))):
            interest = outstanding * monthly_rate
            principal = payment - interest
            if principal <= 0:
                break
            repaid += principal
            outstanding -= principal
        return repaid

    @property
    def roe_patrimonial(self) -> float:
        """ROE patrimonial (%) : Rentabilité incluant le remboursement du capital."""
        annual_capital_repaid = self.principal_repaid_first_n_months(12)
        return ((self.effective_annual_rent - self.monthly_charges * 12 - self.monthly_payment * 12 + annual_capital_repaid) / self.equity * 100) if self.equity > 0 else 0.0

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

    def _evaluate_investment(self, adjusted_debt_ratio: float) -> tuple[str, str, str]:
        """
        Évalue la viabilité de l’investissement avec un score pondéré et
        génère un diagnostic détaillé + conseils.
        Retourne (rec_text, rec_color, rec_details_text).
        """
        score = 0
        details: List[str] = []
        advice: List[str] = []
    
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
    
        # Synthèse
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
    
        return rec_text, rec_color, rec_details_text
        
    def compute(self, inputs: dict) -> dict:
        """
        Calcule toutes les métriques financières et retourne un dictionnaire
        avec uniquement des valeurs numériques et quelques données pour la vue.
        """
        # Charger les inputs dans le modèle
        prop_type = inputs.get("Type de bien", "Ancien")
        self.load_inputs(inputs, prop_type)
    
        # === Core metrics ===
        total_loan_cost = self.monthly_payment * self.n_months
        adjusted_debt_ratio = self.monthly_payment / (self.monthly_income or 1) * 100
    
        # Break-even rent
        break_even_rent = (self.monthly_payment + self.monthly_charges) / (1 - self.gestion_pct / 100)
    
        # Pie data
        pie_data = {
            "Mensualité prêt": self.monthly_payment,
            "Taxe foncière": self.taxe/12,
            "Charges copro": self.copro/12,
            "Gestion agence": self.gestion_pct / 100.0 * self.rent * self.occupancy_rate,
            "GLI": self.gli / 12 * self.occupancy_rate,
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
        for y in range(1, years_int + 1):
            annual_cf = self.monthly_cashflow * 12
            total += annual_cf
            cumulative_cashflow.append(total)
            if total >= 0 and payback_year is None:
                payback_year = y
    
        payback_year = next((i + 1 for i, val in enumerate(cumulative_cashflow) if val >= 0), None)
    
        # === Recommandation factorisée ===
        rec_text, rec_color, rec_details_text = self._evaluate_investment(adjusted_debt_ratio)
    
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
            "adjusted_debt_ratio": adjusted_debt_ratio,
            "pie_data": pie_data,
            "cumulative_cashflow": cumulative_cashflow,
            "payback_year": payback_year,
            "rec_text": rec_text,
            "rec_color": rec_color,
            "rec_details_text": rec_details_text,
            "cashflow": self.monthly_cashflow,
            "taux_couv": self.taux_couv,
            "debt_ratio": adjusted_debt_ratio,
        }
