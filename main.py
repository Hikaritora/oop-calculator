import tkinter as tk

from controller.calculator_controller import CalculatorController
from view.calculator_view import CalculatorView

if __name__ == "__main__":
    root = tk.Tk()
    controller = CalculatorController()
    view = CalculatorView(root, controller)
    root.mainloop()
