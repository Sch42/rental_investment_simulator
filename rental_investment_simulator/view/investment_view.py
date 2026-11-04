from typing import Dict, Tuple, List, Optional
import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def parse_float_from_entry(entry_widget) -> float:
    """
    Parse a float from a CTkEntry-like widget.
    Accepte la virgule décimale et les espaces ; un champ vide vaut 0.0.
    Lève ValueError si la saisie n'est pas un nombre.
    """
    raw = entry_widget.get()
    s = "" if raw is None else str(raw).replace(",", ".").replace(" ", "").replace("\u00a0", "")
    if s == "":
        return 0.0
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"« {raw} » n'est pas un nombre") from None

# -----------------------
# View
# -----------------------
class InvestmentView(ctk.CTk):
    """
    The GUI (View) using CustomTkinter. Exposes methods for the Presenter to:
      - read input values
      - update indicator labels
      - draw pie chart and payback chart
      - register callbacks (calculate button, pie hover)
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Simulateur d'investissement locatif")
        self.geometry("1280x760")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # UI storage
        self.entries: Dict[str, ctk.CTkEntry] = {}       # clé = nom d'attribut du modèle
        self.entry_labels: Dict[str, str] = {}           # clé = nom d'attribut du modèle
        self.indicators: Dict[str, ctk.CTkLabel] = {}
        self.type_menu: Optional[ctk.CTkOptionMenu] = None
        self.rec_label: Optional[ctk.CTkLabel] = None
        self.rec_info_btn: Optional[ctk.CTkButton] = None

        # matplotlib handles
        self.figure = None
        self.ax = None
        self.canvas = None
        

        self.payback_figure = None
        self.payback_ax = None
        self.payback_canvas = None
        
        self.amort_figure = None
        self.amort_ax = None
        self.amort_canvas = None

        # pie interactivity storage
        self.pie_wedges = []
        self.current_values: Dict[str, float] = {}
        self.center_text = None
        self.explode_arr: List[float] = []
        self._hover_index: Optional[int] = None

        self._create_ui()

    # ---- UI building ----
    def _create_ui(self) -> None:
        """Create all UI widgets and layout."""
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        left = ctk.CTkScrollableFrame(container, width=440)
        left.pack(side="left", fill="y", padx=(0, 12), pady=4)
        right = ctk.CTkFrame(container)
        right.pack(side="right", fill="both", expand=True, padx=(12, 0), pady=4)

        # Property type
        ctk.CTkLabel(left, text="Type de bien", anchor="w").pack(fill="x", padx=8, pady=(6, 2))
        self.type_menu = ctk.CTkOptionMenu(left, values=["Ancien", "Neuf"])
        self.type_menu.set("Ancien")
        self.type_menu.pack(fill="x", padx=8, pady=(0, 8))

        # Sections & inputs
        self._add_section(left, "Infos d'achat", [
            ("price", "Prix d'achat (€):", "69000"),
            ("prix_moyen_m2", "Prix moyen au m² (€ / m²):", "2200"),
            ("furn", "Meubles / électroménager (€):", "0"),
            ("other_fees", "Autres frais (€):", "0"),
            ("renovation", "Rénovation / travaux (€):", "8300"),
            ("surface_carrez", "Surface Carrez (m²):", "18.38"),
            ("surface_non_validee", "Surface non prise en compte (m²):", "7.48"),
        ])

        self._add_section(left, "Charges fixes", [
            ("taxe", "Taxe foncière (€ / an):", "300"),
            ("copro", "Charges copropriété (€ / an):", "360"),
            ("gli", "GLI (€ / an):", "0"),
            ("pno", "Assurance PNO (€ / an):", "0"),
            ("compta", "Frais compta (€ / an):", "0"),
            ("autres", "Autres charges (€ / an):", "360"),
        ])

        self._add_section(left, "Charges variables", [
            ("gestion_pct", "Gestion en agence (% du loyer):", "0"),
            ("maintenance_pct", "Maintenance / réparations (% du prix / an):", "2"),
            ("vacancy_months", "Vacance locative (mois/an):", "0"),
        ])

        self._add_section(left, "Revenus locatifs", [
            ("rent", "Loyer mensuel (€):", "500"),
        ])

        self._add_section(left, "Financement", [
            ("apport", "Apport (€):", "15000"),
            ("monthly_income", "Revenu net mensuel (€):", "2000"),
            ("years", "Durée du prêt (années):", "25"),
            ("rate", "Taux d'intérêt annuel (%):", "3.5"),
            ("ins_rate", "Assurance prêt (%):", "0.2"),
        ])
        
        # Champ pour l’épargne mensuelle
        frame_extra = ctk.CTkFrame(left)
        frame_extra.pack(fill="x", padx=6, pady=2)
        ctk.CTkLabel(frame_extra, text="Épargne mensuelle (€/mois)").pack(side="left", padx=(4, 6))
        self.extra_entry = ctk.CTkEntry(frame_extra, width=120)
        self.extra_entry.pack(side="right", padx=(6, 4))

        # Liste déroulante pour le DPE
        frame_dpe = ctk.CTkFrame(left)
        frame_dpe.pack(fill="x", padx=6, pady=2)
        ctk.CTkLabel(frame_dpe, text="DPE").pack(side="left", padx=(4, 6))
        self.dpe_combo = ctk.CTkComboBox(frame_dpe, values=["A","B","C","D","E","F","G"], width=120)
        self.dpe_combo.set("D")  # valeur par défaut
        self.dpe_combo.pack(side="right", padx=(6, 4))


        calc_btn = ctk.CTkButton(left, text="Calculer")
        calc_btn.pack(pady=18, padx=8, fill="x")

        help_label = ctk.CTkLabel(left, text="→ Cliquez sur '?' dans la conclusion pour voir formule & explication",
                                   text_color="#666", wraplength=360, justify="left")
        help_label.pack(padx=8, pady=(4, 12))

        # RIGHT: recommendation & indicators
        self.rec_frame = ctk.CTkFrame(right)
        self.rec_frame.pack(fill="x", padx=8, pady=(0, 8))
        self.rec_label = ctk.CTkLabel(self.rec_frame, text="Recommandation: -", font=("Helvetica", 13, "bold"),
                                      anchor="w")
        self.rec_label.pack(side="left", padx=8, pady=8)
        self.rec_info_btn = ctk.CTkButton(self.rec_frame, text="?", width=40)
        self.rec_info_btn.pack(side="right", padx=8, pady=8)

        self.conclusion_frame = ctk.CTkFrame(right)
        self.conclusion_frame.pack(fill="x", padx=8, pady=(0, 8))

        grid_left = ctk.CTkFrame(self.conclusion_frame)
        grid_left.pack(side="left", fill="both", expand=True, padx=(0, 4))
        grid_right = ctk.CTkFrame(self.conclusion_frame)
        grid_right.pack(side="right", fill="both", expand=True, padx=(4, 0))

        # Indicators regrouped by section
        indicators_by_section = {
            "📊 Coûts & Prix": [
                "Prix total projet (€):",
                "Frais de notaire (€):",
                "Coût total emprunt / prix (€):",
                "Ratio marché (%):",
                "Prix final au m² (€ / m²):",
            ],
            "💰 Rentabilité": [
                "Rendement brut (%):",
                "Rendement net (%):",
                "Cashflow (€ / mois):",
                "Rendement sur fonds propres (%):",
            ],
            "🏦 Financement & Risques": [
                "Ratio prêt/valeur (%):",
                "Taux de couverture (%):",
                "Loyer seuil de rentabilité (€ / mois):",
                "Taux d’endettement (%):",
                "Charges mensuelles (€):",
            ]
        }

        def create_indicator_rows(frame, section_dict):
            for section, label_list in section_dict.items():
                # section title
                ctk.CTkLabel(frame, text=section, anchor="w",
                             font=("Helvetica", 12, "bold")).pack(fill="x", padx=4, pady=(8, 2))
                # section rows
                for label_text in label_list:
                    row = ctk.CTkFrame(frame)
                    row.pack(fill="x", padx=4, pady=2)
                    lbl = ctk.CTkLabel(row, text=label_text, width=200, anchor="w")
                    lbl.pack(side="left", padx=4)
                    val = ctk.CTkLabel(row, text="-", anchor="w")
                    val.pack(side="left", padx=4)
                    btn = ctk.CTkButton(row, text="?", width=40)
                    btn.pack(side="right", padx=4)
                    self.indicators[label_text] = val

        # Half & half distribution
        left_sections = {
            "📊 Coûts & Prix": indicators_by_section["📊 Coûts & Prix"],
            "💰 Rentabilité": indicators_by_section["💰 Rentabilité"],
        }
        right_sections = {
            "🏦 Financement & Risques": indicators_by_section["🏦 Financement & Risques"],
        }

        create_indicator_rows(grid_left, left_sections)
        create_indicator_rows(grid_right, right_sections)
    
        # Payback figure
        payback_frame = ctk.CTkFrame(right)
        payback_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.payback_figure = plt.Figure(figsize=(6, 2), tight_layout=True)
        self.payback_ax = self.payback_figure.add_subplot(111)
        self.payback_canvas = FigureCanvasTkAgg(self.payback_figure, master=payback_frame)
        self.payback_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Pie figure
        pie_frame = ctk.CTkFrame(right)
        pie_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.figure = plt.Figure(figsize=(6, 5), tight_layout=True)
        self.ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(right=0.62)
        self.canvas = FigureCanvasTkAgg(self.figure, master=pie_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Amortization with prepayment figure
        amort_frame = ctk.CTkFrame(right)
        amort_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.amort_figure = plt.Figure(figsize=(6, 3), tight_layout=True)
        self.amort_ax = self.amort_figure.add_subplot(111)
        self.amort_canvas = FigureCanvasTkAgg(self.amort_figure, master=amort_frame)
        self.amort_canvas.get_tk_widget().pack(fill="both", expand=True)

        self._calculate_button = calc_btn


    def _add_section(self, parent, title: str, fields: List[Tuple[str, str, str]]) -> None:
        """Crée les champs d'une section. Chaque champ : (attribut du modèle, libellé, valeur par défaut)."""
        ctk.CTkLabel(parent, text=title, anchor="w", font=("Helvetica", 12, "bold")).pack(fill="x", padx=8, pady=(8, 2))
        for field_name, label_text, default in fields:
            frame = ctk.CTkFrame(parent)
            frame.pack(fill="x", padx=6, pady=2)
            lbl = ctk.CTkLabel(frame, text=label_text, anchor="w")
            lbl.pack(side="left", padx=(4, 6))
            entry = ctk.CTkEntry(frame, width=120)
            entry.insert(0, default)
            entry.pack(side="right", padx=(6, 4))
            self.entries[field_name] = entry
            self.entry_labels[field_name] = label_text.rstrip(":")

    
    def get_all_inputs(self) -> Dict[str, float]:
        """
        Retourne {nom d'attribut du modèle: valeur saisie}, prêt pour InvestmentModel.from_inputs.
        Lève ValueError en listant les champs non numériques.
        """
        parsed = {}
        errors = []
        for field_name, entry in self.entries.items():
            try:
                parsed[field_name] = parse_float_from_entry(entry)
            except ValueError as exc:
                errors.append(f"{self.entry_labels[field_name]} : {exc}")

        # Champs additionnels
        try:
            parsed["extra_monthly_contrib"] = parse_float_from_entry(self.extra_entry)
        except ValueError as exc:
            errors.append(f"Épargne mensuelle : {exc}")
        parsed["dpe"] = self.dpe_combo.get()

        if errors:
            raise ValueError("\n".join(errors))
        return parsed


    def get_property_type(self) -> str:
        """Return current property type selection."""
        return self.type_menu.get() if self.type_menu is not None else "Ancien"

    def bind_calculate(self, handler):
        """Bind the calculate button to presenter handler."""
        self._calculate_button.configure(command=handler)

    def bind_indicator_help(self, help_callback):
        """
        For each indicator label row, configure its '?' button to call help_callback with the label text.
        The create_indicator_rows created a '?' button but didn't store references; we'll find them by traversal.
        """
        # For simplicity, we rely on the same creation order: iterate through parent frames and find buttons
        # A more robust approach would store the button refs at creation time; left concise here.
        for label_text in list(self.indicators.keys()):
            # find the parent frame of the label widget
            label_widget = self.indicators[label_text]
            parent = label_widget.master
            # find the CTkButton in parent (the '?')
            for child in parent.winfo_children():
                if isinstance(child, ctk.CTkButton) and child.cget("text") == "?":
                    cb = child
                    cb.configure(command=lambda t=label_text: help_callback(t))
                    break

    def set_recommendation_info(self, handler):
        """Bind the recommendation '?' button to handler (presenter will provide content)."""
        if self.rec_info_btn:
            self.rec_info_btn.configure(command=handler)

    def update_recommendation(self, text: str, color: str) -> None:
        """Update the main recommendation label."""
        if self.rec_label:
            self.rec_label.configure(text=f"Recommandation: {text}", text_color=color)

    def show_info_modal(self, title: str, text: str) -> None:
        """
        Small modal to display help/info text (scrollable).
        """
        top = ctk.CTkToplevel(self)
        top.title(title)
        top.geometry("520x320")
        top.transient(self)
        try:
            top.grab_set()
        except Exception:
            pass

        textbox = ctk.CTkTextbox(top, wrap="word", width=500, height=260)
        textbox.insert("0.0", text)
        textbox.configure(state="disabled")
        textbox.pack(fill="both", expand=True, padx=12, pady=12)

        btn = ctk.CTkButton(top, text="Fermer", command=top.destroy)
        btn.pack(pady=(0, 12))

    def show_error(self, title: str, text: str) -> None:
        """Affiche une boîte de dialogue d'erreur."""
        messagebox.showerror(title, text)

    def update_indicator(self, label_text: str, value_text: str, color: Optional[str] = None) -> None:
        """
        Update an indicator entry.
        :param label_text: must match keys used when indicators were created.
        """
        widget = self.indicators.get(label_text)
        if widget:
            if color:
                widget.configure(text=value_text, text_color=color)
            else:
                widget.configure(text=value_text)
                
    def draw_pie(self, data_dict: Dict[str, float]) -> None:
        """
        Draw the pie chart on the view and set up internal state for hover behavior.
        """
        self.ax.clear()
        values = list(data_dict.values())
        labels = list(data_dict.keys())
        self.current_values = data_dict
        self.explode_arr = [0] * len(values)
        self.pie_wedges, _ = self.ax.pie(
            values, labels=None, startangle=90, radius=1,
            wedgeprops=dict(width=0.4, edgecolor='w'), explode=self.explode_arr
        )
        self.ax.set(aspect="equal")
        self.ax.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5))
        # center text
        self.center_text = self.ax.text(0, 0, "", ha="center", va="center", fontsize=12, fontweight='bold')
        self._hover_index = None
        self.canvas.draw()

    def set_pie_hover_handler(self, handler):
        """
        Attach the presenter hover handler to matplotlib motion events.
        Handler signature: handler(event, view)
        """
        # wrap handler so it gets 'self' (view)
        def _on_motion(event):
            handler(event, self)

        self.canvas.mpl_connect("motion_notify_event", _on_motion)

    def update_pie_hover(self, selected_index: Optional[int]) -> None:
        """
        Update pie display when a wedge is hovered or not.
        If selected_index is None -> reset.
        """
        if not self.pie_wedges or selected_index == self._hover_index:
            return  # rien à redessiner : évite un redraw complet à chaque mouvement de souris
        self._hover_index = selected_index
        values = list(self.current_values.values())
        labels = list(self.current_values.keys())

        if selected_index is None:
            self.explode_arr = [0] * len(self.pie_wedges)
        else:
            self.explode_arr = [0.05 if i == selected_index else 0 for i in range(len(self.pie_wedges))]

        self.ax.clear()
        self.pie_wedges, _ = self.ax.pie(
            values, labels=None, startangle=90, radius=1,
            wedgeprops=dict(width=0.4, edgecolor='w'), explode=self.explode_arr
        )
        self.ax.set(aspect="equal")
        self.ax.legend(labels, loc="center left", bbox_to_anchor=(1, 0.5))

        if selected_index is not None:
            val = values[selected_index]
            name = labels[selected_index]
            pct = val / sum(values) * 100 if sum(values) > 0 else 0.0
            self.center_text = self.ax.text(0, 0, f"{name}\n{val:,.0f}€\n({pct:.1f}%)",
                                            ha="center", va="center", fontsize=12, fontweight='bold')
        else:
            self.center_text = self.ax.text(0, 0, "", ha="center", va="center", fontsize=12, fontweight='bold')

        self.canvas.draw()
        
    def draw_payback(self, cumulative_cashflow: List[float], years: int, payback_year: Optional[int]) -> None:
        """Plot the payback bar chart with proper colors and payback line."""
        self.payback_ax.clear()
    
        # Assure that cumulative_cashflow matches 'years'
        if len(cumulative_cashflow) != years:
            # étendre ou tronquer pour éviter erreurs
            cumulative_cashflow = (cumulative_cashflow + [0]*years)[:years]
    
        x = list(range(1, years + 1))
        colors = ['red' if cf < 0 else 'green' for cf in cumulative_cashflow]
    
        self.payback_ax.bar(x, cumulative_cashflow, color=colors, edgecolor='black')
    
        # trace la ligne de payback si elle existe
        if payback_year is not None and 1 <= payback_year <= years:
            self.payback_ax.axvline(payback_year, color='blue', linestyle='--', linewidth=2,
                                    label=f'Payback: {payback_year} ans')
    
        self.payback_ax.axhline(0, color='black', linewidth=0.8)
        self.payback_ax.set_xlabel("Années")
        self.payback_ax.set_ylabel("Cumul Cashflow (€)")
        self.payback_ax.set_title("Payback Period")
        self.payback_canvas.draw()
        
    def draw_amortization_chart(self, simu: List[Dict[str, float]]) -> None:
        """Trace l’évolution du capital restant dû et du patrimoine net avec prépaiement."""
        if not simu:
            return
    
        years = [row["Année"] for row in simu]
        remaining = [row["Capital restant dû"] for row in simu]
        patrimoine = [row["Patrimoine net"] for row in simu]
    
        self.amort_ax.clear()
        self.amort_ax.plot(years, remaining, label="Capital restant dû", color="red", linewidth=2)
        self.amort_ax.plot(years, patrimoine, label="Patrimoine net", color="green", linewidth=2)
        self.amort_ax.set_xlabel("Années")
        self.amort_ax.set_ylabel("€")
        self.amort_ax.set_title("Simulation avec prépaiement (épargne mensuelle)")
        self.amort_ax.legend()
        self.amort_canvas.draw()
