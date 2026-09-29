import tkinter as tk

from view.theme import SCREEN_BG, SCREEN_FG, SCREEN_FG_DIM, BODY_BG, EXPRESSION_FONT


class HistoryView:
    """
    Small popup listing past calculations, newest first.

    Picking an entry hands its result to the on_select callback and closes
    the window. The list is a snapshot taken when the window opens.
    """

    def __init__(self, master, entries, on_select):
        self.on_select = on_select
        # Only the result is restored, so keep it next to the text shown for each row
        self.results = [result for _, result in reversed(entries)]

        self.window = tk.Toplevel(master)
        self.window.title("History")
        self.window.geometry("300x360")
        self.window.configure(background=BODY_BG)
        self.window.transient(master)

        if not entries:
            tk.Label(
                self.window, text="No calculations yet", background=BODY_BG,
                foreground=SCREEN_FG_DIM, font=EXPRESSION_FONT,
            ).pack(expand=True)
            return

        frame = tk.Frame(self.window, background=SCREEN_BG)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(
            frame, yscrollcommand=scrollbar.set, background=SCREEN_BG,
            foreground=SCREEN_FG, font=EXPRESSION_FONT, activestyle="none",
            selectbackground=SCREEN_FG_DIM, selectforeground=SCREEN_FG,
            borderwidth=0, highlightthickness=0, relief="flat",
        )
        self.listbox.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.config(command=self.listbox.yview)

        for expression, result in reversed(entries):
            # "/" is stored as the logical symbol, but shown as ÷ like on the keypad
            self.listbox.insert("end", f"{expression.replace('/', '÷')} = {result}")

        self.listbox.bind("<<ListboxSelect>>", self._on_pick)

    def _on_pick(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        result = self.results[selection[0]]
        self.window.destroy()
        self.on_select(result)
