import tkinter as tk

from gui import MiniJFLAP


def main():
    root = tk.Tk()
    app = MiniJFLAP(root)
    root.mainloop()


if __name__ == "__main__":
    main()
