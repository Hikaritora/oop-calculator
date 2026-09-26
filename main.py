import ttkbootstrap as ttk

from controller.calculator_controller import CalculatorController
from view.calculator_view import CalculatorView

if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    controller = CalculatorController()
    view = CalculatorView(root, controller)
    root.mainloop()
