from model.investment_model import InvestmentModel
from view.investment_view import InvestmentView
from presenter.investment_presenter import InvestmentPresenter


def main() -> None:
    model = InvestmentModel()
    view = InvestmentView()
    presenter = InvestmentPresenter(model, view)
    view.mainloop()


if __name__ == "__main__":
    main()
