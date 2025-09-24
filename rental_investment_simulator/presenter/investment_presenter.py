from tkinter import messagebox
from typing import Dict, Any
from model.investment_model import InvestmentModel, safe_parse_float, color_gradient, VALORISATION_NON_CARREZ
from view.investment_view import InvestmentView
import matplotlib.pyplot as plt
import os
# -----------------------
# Presenter
# -----------------------
class InvestmentPresenter:
    """
    The Presenter reads the inputs from View, calls the Model, and updates the View.
    """

    def __init__(self, model: InvestmentModel, view: InvestmentView) -> None:
        self.model = model
        self.view = view
        # bind UI events
        self.view.bind_calculate(self.on_calculate)
        self.view.set_pie_hover_handler(self.on_pie_motion)
        self.view.bind_indicator_help(self.on_indicator_help)
        # set rec info handler placeholder
        self.rec_details_text = ""
        self.view.set_recommendation_info(self.show_recommendation_details)
        self.generate_investment_report()

    def on_calculate(self) -> None:
        """Triggered when the user clicks 'Calculer'."""
        try:
            inputs = self.view.get_all_inputs()
            prop_type = self.view.get_property_type()
            results = self.model.compute(inputs)
            
            # update recommendation
            self.view.update_recommendation(results["rec_text"], results["rec_color"])
            self.rec_details_text = results["rec_details_text"] + "\n\n" + self._recommendation_explanation(results)
            self.view.set_recommendation_info(self.show_recommendation_details)

            # update indicators (keeps same label keys as created)
            self.view.update_indicator("Cashflow (€ / mois):", f"{results['monthly_cashflow']:,.2f}€",
                                       color=self._color_cashflow(results['monthly_cashflow'], results['monthly_payment'], safe_parse_float(inputs.get("Revenu net mensuel (€)", 0.0))))
            self.view.update_indicator("Rendement brut (%):", f"{results['gross_yield']:.2f}%",
                                       color=color_gradient(results['gross_yield'], (5, 8, 15)))
            self.view.update_indicator("Rendement net (%):", f"{results['net_yield']:.2f}%",
                                       color=color_gradient(results['net_yield'], (3, 5, 10)))
            self.view.update_indicator("Taux de couverture (%):", f"{results['taux_couv']:.2f}%",
                           color=color_gradient(results['taux_couv'], (70, 85, 100), ("red", "orange", "green")))
            self.view.update_indicator("Loyer seuil de rentabilité (€ / mois):", f"{results['break_even_rent']:,.2f}€")
            self.view.update_indicator("Ratio prêt/valeur (%):", f"{results['ltv']:.2f}%",
                                       color=color_gradient(results['ltv'], (80, 90, 100), ("green", "orange", "red")))
            self.view.update_indicator("Rendement sur fonds propres (%):", f"{results['roe']:.2f}%",
                                       color=color_gradient(results['roe'], (3, 5, 10)))
            self.view.update_indicator("Prix final au m² (€ / m²):", f"{results['price_carrez']:,.0f}€ (prix m² pondéré: {results['price_total_pondere']:,.0f}€)",
                                       color=color_gradient(results['price_carrez'], (2000, 3000, 5000)))
            self.view.update_indicator("Prix total projet (€):", f"{results['total_project']:,.0f}€")
            self.view.update_indicator("Coût total emprunt / prix (€):", f"{results['total_loan_cost']:,.0f}€ ({results['loan_ratio']:.1f}%)",
                                       color=color_gradient(results['loan_ratio'], (130, 150, 200), ("green", "orange", "red")))
            self.view.update_indicator("Frais de notaire (€):", f"{results['notary']:,.0f}€")
            self.view.update_indicator("Charges mensuelles (€):", f"{results['monthly_charges']:,.0f}€")
            self.view.update_indicator("Taux d’endettement (%):", f"{results['adjusted_debt_ratio']:.1f}%",
                                       color=color_gradient(results['adjusted_debt_ratio'], (30, 35, 50), ("green", "orange", "red")))
            self.view.update_indicator("Ratio marché (%):", f"{results['ratio_marche']:.1f}%",
                                       color=color_gradient(results['ratio_marche'], (100, 110, 120), ("green", "orange", "red")))
            
            # Générer le rapport maintenant que tout est calculé
            self.generate_investment_report()
            
            
            # --- Simulation amortissement avec prépaiement ---
            simu = self.model.simulate_amortization(int(self.model.years))
            self.view.draw_amortization_chart(simu)
            
            

            
            # pie chart and payback
            pie_file = "charges_pie.png"
            payback_file = "payback_period.png"
            self.save_charts(pie_file, payback_file)
            self.view.draw_pie(results['pie_data'])
            self.view.draw_payback(results['cumulative_cashflow'], int(self.model.years), results['payback_year'])


        except Exception as exc:
            messagebox.showerror("Erreur", f"Veuillez entrer des nombres valides.\n{str(exc)}")
        

    def _color_cashflow(self, cashflow: float, monthly_payment: float, monthly_income: float) -> str:
        """
        Return a color string based on cashflow, replicating the original logic.
        """
        if cashflow < 0:
            return "red"
        coverage_ratio = cashflow / monthly_payment if monthly_payment > 0 else 0
        income_ratio = cashflow / monthly_income if monthly_income > 0 else 0
        if coverage_ratio < 0.2 or income_ratio < 0.05:
            return "orange"
        if coverage_ratio < 0.5 or income_ratio < 0.1:
            return "yellow"
        if coverage_ratio < 1.0 or income_ratio < 0.2:
            return "green"
        return "darkgreen"

    def on_pie_motion(self, event, view: InvestmentView) -> None:
        """
        Mouse motion handler for the pie. Checks which wedge (if any) contains
        the mouse and asks the view to update the explode/center text.
        """
        try:
            if not view.pie_wedges:
                return
            contains_any = False
            # Matplotlib's contains_point expects display coordinates; wedge.contains_point accepts tuple
            for i, wedge in enumerate(view.pie_wedges):
                if wedge.contains_point([event.x, event.y]):
                    contains_any = True
                    view.update_pie_hover(i)
                    break
            if not contains_any:
                view.update_pie_hover(None)
        except Exception:
            # silently ignore motion errors (keeps behavior smooth)
            pass

    def on_indicator_help(self, label_text: str) -> None:
        """
        Show formula/explanation for an indicator label.
        Mirrors original get_formula_explanation logic.
        """
        explanation = self._get_formula_explanation(label_text)
        self.view.show_info_modal(label_text, explanation)

    def show_recommendation_details(self) -> None:
        """Display the stored recommendation details modal."""
        if self.rec_details_text:
            self.view.show_info_modal("Détails de la recommandation", self.rec_details_text)
        else:
            self.view.show_info_modal("Détails de la recommandation", "Pas de détails disponibles.")

    # ---- Explanations (copied / adapted from original) ----
    @staticmethod
    def _recommendation_explanation(summary: Dict[str, Any]) -> str:
        txt = (
            "Recommandations détaillées :\n\n"
            "Vert : indicateur bon, projet confortable.\n"
            "Orange : marge de sécurité réduite.\n"
            "Rouge : projet risqué.\n\n"
        )
        if summary:
            txt += "--- Résumé du projet ---\n"
            txt += f"Cashflow : {summary.get('cashflow', 0):.0f} €/mois\n"
            txt += f"Taux de couverture : {summary.get('taux_couv', 0):.1f} %\n"
            txt += f"LTV : {summary.get('ltv', 0):.1f} %\n"
            txt += f"Taux d’endettement : {summary.get('debt_ratio', 0):.1f} %\n"
            txt += f"Ratio marché : {summary.get('ratio_marche', 0):.1f} %\n\n"
        txt += (
            "--- Interprétation ---\n"
            "- Cashflow ≥0 : projet s’autofinance.\n"
            "- Taux de couverture ≤70 % : bon équilibre loyer/crédit.\n"
            "- Loyer seuil de rentabilité ≤80 % : ratio prêt/valeur sûr.\n"
            "- Endettement ≤30 % : soutenable.\n\n"
            "- Ratio marché <100 % : bien sous le prix du marché.\n"
            "Conseils :\n"
            "- En cas de Rouge : augmenter l’apport, négocier le prix ou rehausser le loyer.\n"
            "- En cas de Orange : vérifier charges et prévoir une marge de sécurité."
        )
        return txt
    
    def _recommendation_explanation(self, summary: Dict[str, Any]) -> str:
        w = self.model.scoring_weights  # pondérations dynamiques
    
        txt = (
            "Recommandations détaillées :\n\n"
            "🟢 Vert : indicateur bon, projet confortable.\n"
            "🟡 Orange : marge de sécurité réduite.\n"
            "🔴 Rouge : projet risqué.\n\n"
        )
    
        if summary:
            txt += "--- Résumé du projet ---\n"
            txt += f"Cashflow : {summary.get('cashflow', 0):.0f} €/mois\n"
            txt += f"Taux de couverture : {summary.get('taux_couv', 0):.1f} %\n"
            txt += f"LTV : {summary.get('ltv', 0):.1f} %\n"
            txt += f"Taux d’endettement : {summary.get('debt_ratio', 0):.1f} %\n"
            txt += f"Ratio marché : {summary.get('ratio_marche', 0):.1f} %\n\n"
    
        txt += "--- Grille de scoring (pondération /100) ---\n"
        txt += (
            f"1. 💰 Cashflow ({w['cashflow']} pts)\n"
            f"   > 100 € : {w['cashflow']}/{w['cashflow']} → projet confortable.\n"
            f"   0–100 € : {w['cashflow']//2}/{w['cashflow']} → autofinancement partiel, peu de marge.\n"
            f"   < 0 €   : 0/{w['cashflow']} → déficit mensuel, risque immédiat.\n\n"
    
            f"2. 📈 Rendement net ({w['net_yield']} pts)\n"
            f"   ≥ 5 %   : {w['net_yield']}/{w['net_yield']} → investissement performant.\n"
            f"   3–5 %   : {w['net_yield']*3//5}/{w['net_yield']} → rendement correct mais améliorable.\n"
            f"   < 3 %   : {w['net_yield']//5}/{w['net_yield']} → projet faiblement rentable (non nul car il reste un revenu brut locatif).\n\n"
    
            f"3. 🏷️ Ratio marché ({w['ratio_marche']} pts)\n"
            f"   ≤ 95 %  : {w['ratio_marche']}/{w['ratio_marche']} → bonne affaire (sous-évalué).\n"
            f"   95–105 %: {w['ratio_marche']*2//3}/{w['ratio_marche']} → prix conforme au marché.\n"
            f"   > 105 % : 0/{w['ratio_marche']} → surpayé, risque de perte en cas de revente.\n\n"
    
            f"4. 🏦 Endettement ajusté ({w['debt_ratio']} pts)\n"
            f"   ≤ 30 %  : {w['debt_ratio']}/{w['debt_ratio']} → soutenable.\n"
            f"   30–40 % : {w['debt_ratio']//2}/{w['debt_ratio']} → faisable mais attention à la capacité d’emprunt.\n"
            f"   > 40 %  : 0/{w['debt_ratio']} → surendettement probable, alerte rouge.\n\n"
    
            f"5. 📊 LTV ({w['ltv']} pts)\n"
            f"   ≤ 80 %  : {w['ltv']}/{w['ltv']} → apport suffisant, marge de sécurité.\n"
            f"   80–90 % : {w['ltv']//2}/{w['ltv']} → dépendance accrue au financement bancaire.\n"
            f"   > 90 %  : 0/{w['ltv']} → risque élevé, trop peu d’apport.\n\n"
        )
    
        txt += (
            "--- Conseils pratiques ---\n"
            "- Rouge sur Cashflow : négocier le prix, augmenter l’apport ou optimiser la gestion locative.\n"
            "- Rouge sur Rendement : revoir le prix d’achat, cibler un meilleur marché ou améliorer le loyer.\n"
            "- Rouge sur Ratio marché : bien trop cher, envisager une autre opportunité.\n"
            "- Rouge sur Endettement : réduire le crédit ou augmenter l’apport.\n"
            "- Rouge sur LTV : viser plus de fonds propres pour réduire le risque.\n"
        )
    
        return txt

    def generate_investment_report(self, filename: str = "rapport_investissement.txt") -> str:
        """
        Génère un fichier texte détaillé avec les résultats de la simulation.
        Structure optimisée pour présenter le projet à une banque.
        """
        results = self.model.compute({
            "Type de bien": self.model.type_of_property,
            "Prix d'achat": self.model.price,
            "Meubles": self.model.furn,
            "Autres frais": self.model.other_fees,
            "Rénovation": self.model.renovation,
            "Surface Carrez": self.model.surface_carrez,
            "Surface non prise en compte": self.model.surface_non_validee,
            "Taxe foncière": self.model.taxe,
            "Charges copro": self.model.copro,
            "Gestion en agence": self.model.gestion_pct,
            "GLI": self.model.gli,
            "Assurance PNO": self.model.pno,
            "Frais compta": self.model.compta,
            "Autres charges": self.model.autres,
            "Maintenance": self.model.maintenance_pct,
            "Vacance locative": self.model.vacancy_months,
            "Loyer": self.model.rent,
            "Apport": self.model.apport,
            "Revenu net mensuel": self.model.monthly_income,
            "Durée": self.model.years,
            "Taux d'intérêt": self.model.rate * 100,
            "Assurance prêt": self.model.ins_rate * 100,
            "Prix moyen": self.model.prix_moyen_m2
        })
    
        self.fixed_charges = {
            "Taxe foncière": self.model.taxe / 12,
            "Charges copro": self.model.copro / 12,
            "Assurance PNO": self.model.pno / 12,
            "Frais compta": self.model.compta / 12,
            "Autres charges": self.model.autres / 12,
        }
    
        self.variable_charges = {
            "Gestion agence": (self.model.gestion_pct / 100) * self.model.rent * self.model.occupancy_rate,
            "Maintenance": self.model.maintenance / 12,
            "Vacance locative (impact)": (1 - self.model.occupancy_rate) * self.model.rent,
            "GLI": self.model.gli / 12,
        }
    
        with open(filename, "w", encoding="utf-8") as f:
            # === TITRE ===
            f.write("=== 📑 Dossier d’Investissement Locatif ===\n\n")
    
            # --- Infos projet ---
            f.write("=== 🏠 Informations sur le bien ===\n")
            f.write(f"Type de bien : {self.model.type_of_property}\n")
            f.write(f"Prix d'achat : {self.model.price:,.0f} €\n")
            f.write(f"Coût total projet : {results['total_project']:,.0f} €\n")
            f.write(f"Surface Carrez : {self.model.surface_carrez:.2f} m²\n")
            f.write(f"Surface pondérée : {self.model.surface_totale_ponderee:.2f} m²\n")
            f.write(f"Prix moyen secteur : {self.model.prix_moyen_m2:,.0f} €/m²\n")
            f.write(f"Ratio marché : {results['ratio_marche']:.2f} %\n\n")
    
            # --- Financement ---
            f.write("=== 💶 Financement ===\n")
            f.write(f"Apport personnel : {self.model.apport:,.0f} €\n")
            f.write(f"Montant emprunté : {self.model.loan_amount:,.0f} €\n")
            f.write(f"Durée du prêt : {self.model.years} ans ({self.model.n_months} mois)\n")
            f.write(f"Mensualité totale : {self.model.monthly_payment:,.2f} €/mois\n")
            f.write(f"Taux d'intérêt : {self.model.rate*100:.2f} %\n")
            f.write(f"Taux assurance : {self.model.ins_rate*100:.2f} %\n\n")
    
            # --- Charges ---
            f.write("=== 📌 Charges fixes (€/mois) ===\n")
            for k, v in self.fixed_charges.items():
                f.write(f"- {k}: {v:.2f}\n")
            f.write(f"Total charges fixes : {sum(self.fixed_charges.values()):.2f} €/mois\n\n")
    
            f.write("=== 📈 Charges variables (€/mois) ===\n")
            for k, v in self.variable_charges.items():
                f.write(f"- {k}: {v:.2f}\n")
            f.write(f"Total charges variables : {sum(self.variable_charges.values()):.2f} €/mois\n\n")
    
            # --- Indicateurs financiers ---
            f.write("=== 📊 Indicateurs financiers ===\n")
            f.write(f"Cashflow net mensuel : {results['monthly_cashflow']:.2f} €\n")
            f.write(f"Rendement brut : {results['gross_yield']:.2f} %\n")
            f.write(f"Rendement net : {results['net_yield']:.2f} %\n")
            f.write(f"Taux de couverture : {results['taux_couv']:.2f} %\n")
            f.write(f"LTV (projet) : {results['ltv']:.2f} %\n")
            f.write(f"ROE (cashflow) : {results['roe']:.2f} %\n\n")
    
            # --- Analyse et recommandations ---
            f.write("=== 🧾 Analyse & Recommandations ===\n")
            f.write(f"🔹 Synthèse : {results['rec_text']}\n")
            f.write("🔹 Optimisation / plan d’action :\n")
            f.write("- Vérifier possibilité de renégociation du prix ou augmentation apport\n")
            f.write("- Optimiser travaux / rénovation pour augmenter rendement\n")
            f.write("- Ajuster loyer si nécessaire pour couvrir charges et mensualités\n")
            f.write("- Valider financement (durée, taux, assurance) pour sécuriser le projet\n")
            f.write("🔹 Points d’attention : vacance locative, charges imprévues, marché local\n")
            f.write(f"{results['rec_details_text']}\n\n")
    
            # --- Conclusion pour la banque ---
            f.write("=== ✅ Conclusion pour la banque ===\n")
            f.write("- Projet cohérent et sécurisé avec ratios financiers conformes aux standards bancaires\n")
            f.write("- Gestion proactive des risques avec marge de sécurité intégrée\n")
            f.write("- Cashflow positif ou déficit faible compensé par apport ou revenu personnel\n")
                        # --- Ajouter les graphiques ---
            pie_file = "charges_pie.png"
            payback_file = "payback_period.png"
            self.save_charts(pie_file, payback_file)
            
            f.write("=== 📊 Graphiques visuels ===\n")
            f.write(f"- Répartition des charges : voir {pie_file}\n")
            f.write(f"- Payback period : voir {payback_file}\n")
            f.write("Ces graphiques permettent de visualiser rapidement la maîtrise des coûts et la période de retour sur investissement.\n")

        return os.path.abspath(filename)
    



    @staticmethod
    def _get_formula_explanation(label_text: str) -> str:
        """
        Provide textual explanations for each indicator as in the original script,
        updated to match the actual formulas implemented in InvestmentModel,
        with additional investor insights.
        """
        
        
        formulas = {
            "Prix total projet (€):": (
                "Le prix total projet correspond à tous les coûts liés à l'achat et à la mise en état du bien.\n"
                "Cela inclut : le prix du bien, les frais de notaire, les meubles/électroménager, "
                "les autres frais (diagnostics, agence…) et les travaux ou rénovations.\n\n"
                "Formule :\nPrix total projet = Prix du bien + Frais de notaire + Meubles/électroménager + Autres frais + Rénovation/Travaux\n\n"
                "💡 Conseil investisseur : ce coût doit être comparé au budget total disponible et au financement bancaire. "
                "N’oubliez pas de prévoir une marge de sécurité pour les imprévus."
            ),
            "Prix final au m² (€ / m²):": (
                "Le prix final au m² permet de comparer le coût du bien avec le marché.\n"
                "Formule :\nPrix final au m² = Prix total projet / Surface pondérée\n\n"
                "La surface pondérée inclut la surface Carrez + 30% des surfaces non Carrez.\n\n"
                "💡 Attention : certains marchés (ex. Paris) valorisent beaucoup les surfaces non Carrez "
                "tandis que dans d’autres régions rurales, elles sont peu valorisées."
            ),
            "Cashflow (€ / mois):": (
                "Le cashflow correspond à l'argent restant chaque mois après avoir payé toutes les charges et la mensualité du prêt.\n"
                "Formule :\nCashflow = Loyer mensuel effectif - Charges mensuelles - Mensualité du prêt\n\n"
                "💡 Objectif : un cashflow positif assure la solidité de votre investissement. "
                "Un cashflow négatif peut être acceptable si vous anticipez une forte plus-value."
            ),
            "Frais de notaire (€):": (
                "Frais de notaire = Prix du bien × Taux notaire\n"
                "- Ancien : ~8%\n- Neuf : ~2,5%\n\n"
                "💡 Attention : les frais de notaire varient selon la région (droits départementaux et communaux), "
                "et peuvent légèrement dépasser ces moyennes. "
                "Certains frais (honoraires d’agence) peuvent aussi être inclus dans la base taxable."
            ),
            "Charges mensuelles (€):": (
                "Charges mensuelles = (Taxe foncière + Copropriété + GLI + PNO + Compta + Autres + Maintenance) / 12\n"
                "+ Gestion en agence (calculée sur le loyer effectif perçu).\n\n"
                "💡 Conseil : vérifiez le montant des charges de copropriété (syndic), "
                "elles peuvent fortement impacter la rentabilité."
            ),
            "Ratio marché (%):": (
                "Ratio marché = Prix au m² pondéré / Prix moyen au m² du marché × 100\n\n"
                "💡 Un ratio <100% signifie que vous achetez sous le prix du marché (bon point). "
                "Un ratio >120% peut indiquer un bien trop cher ou une erreur dans l’évaluation."
            ),
            "Rendement brut (%):": (
                "Rendement brut = Loyer annuel effectif / Prix total projet × 100\n\n"
                "💡 Sert à comparer rapidement plusieurs biens, mais ne tient pas compte des charges."
            ),
            "Rendement net (%):": (
                "Rendement net = (Loyer annuel effectif - Charges annuelles) / Prix total projet × 100\n\n"
                "💡 C’est l’indicateur clé pour mesurer la rentabilité réelle. "
                "Un rendement net >5% est généralement considéré comme bon en France."
            ),
            "Taux de couverture (%):": (
                "Taux de couverture = (Loyer effectif mensuel / Mensualité totale) × 100\n\n"
                "💡 Un taux de couverture ≥100% signifie que le crédit est couvert par le loyer. "
                "En dessous, vous devrez compléter avec vos revenus."
            ),
            "Rendement sur fonds propres (%):": (
                "ROE Cashflow = (Loyer annuel effectif - Charges annuelles - Mensualités) / Fonds propres investis × 100\n"
                "ROE Patrimonial ajoute le capital remboursé dans le calcul.\n\n"
                "💡 C’est l’indicateur préféré des investisseurs car il mesure la rentabilité réelle de l’argent investi."
            ),
            "Coût total emprunt / prix (€):": (
                "Le coût total de l'emprunt = Mensualité × Nombre de mois\n\n"
                "💡 Ce montant inclut capital + intérêts + assurance. "
                "Comparer plusieurs durées de prêt permet d’équilibrer mensualité et coût total."
            ),
            "Taux d’endettement (%):": (
                "Taux d’endettement = (Mensualité totale - Loyer effectif mensuel) / Revenu net mensuel × 100\n\n"
                "💡 La banque accepte en général un taux ≤35%. "
                "Si votre bien a un taux d’endettement élevé, il sera plus difficile d’obtenir un nouveau crédit."
            ),
            "Loyer seuil de rentabilité (€ / mois):": (
                "Le Loyer seuil de rentabilité est le loyer minimum à percevoir pour couvrir toutes les charges et la mensualité du prêt.\n"
                "Formule :\nLoyer seuil = (Mensualité du prêt + Charges mensuelles) / (1 - % gestion en agence)\n\n"
                "💡 Pratique : cela permet d’évaluer rapidement si le loyer du marché est suffisant pour rendre l’opération viable."
            ),
            "Ratio prêt/valeur (%):": (
                "LTV Prix = Montant du prêt / Prix du bien × 100\n\n"
                "💡 Les banques préfèrent un LTV ≤90%. "
                "Au-delà, vous devrez souvent augmenter l’apport."
            ),
            "Loan-to-Value projet (%):": (
                "LTV Projet = Montant du prêt / Prix total projet × 100\n\n"
                "💡 Cet indicateur est plus complet car il inclut les frais annexes dans l’analyse."
            ),
            "Equity (€):": (
                "Equity = Apport + Frais de notaire + Rénovation + Meubles + Autres frais\n\n"
                "💡 Plus votre equity est élevé, moins vous êtes dépendant du financement bancaire."
            )
        }
        return formulas.get(label_text, "Aucune information disponible pour cet indicateur.")

    

    def save_charts(self, pie_filename="charges_pie.png", payback_filename="payback_period.png"):
        """
        Save pie chart of charges and payback period chart.
        Handles empty or zero data gracefully.
        """
        # --- Pie chart charges ---
        all_charges = {**getattr(self, 'fixed_charges', {}), **getattr(self, 'variable_charges', {})}
        labels = list(all_charges.keys())
        values = list(all_charges.values())
    
        if not values or sum(values) == 0:
            # Handle empty or all-zero charges
            labels = ["Aucune charge"]
            values = [1]
    
        fig, ax = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct=lambda pct: f"{pct:.1f}%\n({pct/100*sum(values):.0f}€)",
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor='w')
        )
        ax.set_title("Répartition des charges mensuelles")
        plt.savefig(pie_filename, bbox_inches='tight')
        plt.close(fig)
    
        # --- Payback period ---
        cumulative_cashflow = getattr(self.model, 'cumulative_cashflow', [])
        years = int(getattr(self.model, 'years', 1))
        payback_year = getattr(self.model, 'payback_year', None)
    
        if not cumulative_cashflow or all(cf == 0 for cf in cumulative_cashflow):
            # Handle empty or all-zero cashflow
            cumulative_cashflow = [0] * years
    
        x = list(range(1, years + 1))
        colors = ['green' if cf >= 0 else 'red' for cf in cumulative_cashflow]
    
        fig2, ax2 = plt.subplots(figsize=(8, 3))
        ax2.bar(x, cumulative_cashflow, color=colors, edgecolor='black')
        if payback_year:
            ax2.axvline(payback_year, color='blue', linestyle='--', label=f'Payback: {payback_year} ans')
        ax2.axhline(0, color='black', linewidth=0.8)
        ax2.set_xlabel("Années")
        ax2.set_ylabel("Cumul Cashflow (€)")
        ax2.set_title("Payback Period")
        if payback_year:
            ax2.legend()
        plt.savefig(payback_filename, bbox_inches='tight')
        plt.close(fig2)



# -----------------------
# Run Application
# -----------------------
def main() -> None:
    model = InvestmentModel()
    view = InvestmentView()
    presenter = InvestmentPresenter(model, view)
    view.mainloop()


if __name__ == "__main__":
    main()
