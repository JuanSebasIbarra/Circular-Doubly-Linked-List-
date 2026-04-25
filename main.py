import tkinter as tk
from model import ClockModel
from view.clock_view import ClockView
from controller.clock_controller import ClockController


def main() -> None:
    root = tk.Tk()

    model = ClockModel()
    view = ClockView(root)
    controller = ClockController(root, model, view)

    controller.start()
    root.mainloop()


if __name__ == "__main__":
    main()