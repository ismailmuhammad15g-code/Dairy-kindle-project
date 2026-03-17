#!/usr/bin/env python3
"""
Zetsu Diary - A native diary application for Jailbroken Amazon Kindle devices.

Designed for E-ink displays:
  - High-contrast black and white interface only.
  - Large, readable fonts.
  - No animations or visual effects.

Notes are saved as timestamped .txt files in /mnt/us/documents/Zetsu_Notes/.
"""

import tkinter as tk
import datetime
import os
import re


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NOTES_DIR = "/mnt/us/documents/Zetsu_Notes"

# Colors — strict black/white for E-ink display compatibility
BG_COLOR = "#FFFFFF"       # white background
FG_COLOR = "#000000"       # black text
BTN_BG   = "#000000"       # black button background
BTN_FG   = "#FFFFFF"       # white button text

# Fonts — large and easy to read on an E-ink screen
FONT_TEXT   = ("DejaVu Sans", 18)
FONT_ENTRY  = ("DejaVu Sans", 20)
FONT_BUTTON = ("DejaVu Sans", 20, "bold")
FONT_TITLE  = ("DejaVu Sans", 24, "bold")
FONT_STATUS = ("DejaVu Sans", 14)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
class ZetsuDiaryApp:
    """Main application window for Zetsu Diary."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._configure_root()
        self._build_ui()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _configure_root(self) -> None:
        """Configure the main window for E-ink display."""
        self.root.title("Zetsu Diary")
        self.root.configure(bg=BG_COLOR)
        # Full-screen is ideal for Kindle; fall back gracefully on desktop.
        self.root.attributes("-fullscreen", True)
        # Disable window decorations / animations
        self.root.resizable(False, False)
        # Bind Escape key to exit (useful for testing on desktop)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

    def _build_ui(self) -> None:
        """Build all UI widgets."""
        # --- Title bar ---------------------------------------------------
        title_label = tk.Label(
            self.root,
            text="✏  Zetsu Diary",
            font=FONT_TITLE,
            bg=BG_COLOR,
            fg=FG_COLOR,
            pady=10,
        )
        title_label.pack(fill=tk.X, side=tk.TOP)

        # Horizontal separator
        separator_top = tk.Frame(self.root, bg=FG_COLOR, height=2)
        separator_top.pack(fill=tk.X, side=tk.TOP)

        # --- Title entry -------------------------------------------------
        title_row = tk.Frame(self.root, bg=BG_COLOR)
        title_row.pack(fill=tk.X, padx=20, pady=(12, 4))

        title_label = tk.Label(
            title_row,
            text="Title:",
            font=FONT_ENTRY,
            bg=BG_COLOR,
            fg=FG_COLOR,
        )
        title_label.pack(side=tk.LEFT, padx=(0, 10))

        self.title_entry = tk.Entry(
            title_row,
            font=FONT_ENTRY,
            bg=BG_COLOR,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,
            relief=tk.SOLID,
            bd=2,
            selectbackground=FG_COLOR,
            selectforeground=BG_COLOR,
        )
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Thin separator between title row and text area
        separator_mid = tk.Frame(self.root, bg=FG_COLOR, height=1)
        separator_mid.pack(fill=tk.X, padx=20, pady=(4, 0))

        # --- Text area ---------------------------------------------------
        text_frame = tk.Frame(self.root, bg=BG_COLOR)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 5))

        self.text_widget = tk.Text(
            text_frame,
            font=FONT_TEXT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            insertbackground=FG_COLOR,   # cursor colour
            relief=tk.SOLID,
            bd=2,
            wrap=tk.WORD,
            undo=True,
            # Disable all cursor/selection highlights that could cause grey
            selectbackground=FG_COLOR,
            selectforeground=BG_COLOR,
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        self.text_widget.focus_set()

        # --- Bottom separator -------------------------------------------
        separator_bottom = tk.Frame(self.root, bg=FG_COLOR, height=2)
        separator_bottom.pack(fill=tk.X, side=tk.BOTTOM)

        # --- Info bar (version stamp) ------------------------------------
        info_bar = tk.Label(
            self.root,
            text="Zetsuserv Core v1.0",
            font=FONT_STATUS,
            bg=BG_COLOR,
            fg=FG_COLOR,
            anchor=tk.CENTER,
            pady=2,
        )
        info_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # --- Status bar --------------------------------------------------
        self.status_var = tk.StringVar(value="Ready — write your diary entry above.")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=FONT_STATUS,
            bg=BG_COLOR,
            fg=FG_COLOR,
            anchor=tk.W,
            padx=20,
            pady=4,
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # --- Button row --------------------------------------------------
        button_frame = tk.Frame(self.root, bg=BG_COLOR, pady=10)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20)

        save_button = tk.Button(
            button_frame,
            text="💾  Save Entry",
            font=FONT_BUTTON,
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=FG_COLOR,
            activeforeground=BG_COLOR,
            relief=tk.SOLID,
            bd=2,
            padx=30,
            pady=12,
            command=self._save_entry,
        )
        save_button.pack(side=tk.LEFT, padx=(0, 10))

        clear_button = tk.Button(
            button_frame,
            text="🗑  Clear",
            font=FONT_BUTTON,
            bg=BG_COLOR,
            fg=FG_COLOR,
            activebackground=FG_COLOR,
            activeforeground=BG_COLOR,
            relief=tk.SOLID,
            bd=2,
            padx=30,
            pady=12,
            command=self._clear_text,
        )
        clear_button.pack(side=tk.LEFT, padx=(0, 10))

        exit_button = tk.Button(
            button_frame,
            text="✖  Exit",
            font=FONT_BUTTON,
            bg=BG_COLOR,
            fg=FG_COLOR,
            activebackground=FG_COLOR,
            activeforeground=BG_COLOR,
            relief=tk.SOLID,
            bd=2,
            padx=30,
            pady=12,
            command=lambda: self._ask_confirm("Are you sure?", self.root.destroy),
        )
        exit_button.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Confirmation dialog
    # ------------------------------------------------------------------
    def _ask_confirm(self, question: str, on_yes) -> None:
        """Show a custom modal confirmation dialog.

        Avoids tkinter.messagebox which can be unreliable on Kindle/X11.
        The dialog is centered on screen, has a thick black border on a
        white background, and presents Yes / No buttons.
        """
        dialog = tk.Toplevel(self.root)
        dialog.configure(bg=BG_COLOR, bd=6, relief=tk.SOLID)
        dialog.resizable(False, False)
        # Keep it on top of the main window
        dialog.transient(self.root)

        # Question label
        tk.Label(
            dialog,
            text=question,
            font=FONT_ENTRY,      # DejaVu Sans 20 pt
            bg=BG_COLOR,
            fg=FG_COLOR,
            padx=40,
            pady=30,
            wraplength=500,
        ).pack()

        # Thin separator
        tk.Frame(dialog, bg=FG_COLOR, height=2).pack(fill=tk.X)

        # Button row
        btn_frame = tk.Frame(dialog, bg=BG_COLOR, pady=20)
        btn_frame.pack()

        def _yes() -> None:
            dialog.destroy()
            on_yes()

        def _no() -> None:
            dialog.destroy()

        tk.Button(
            btn_frame,
            text="  Yes  ",
            font=FONT_BUTTON,
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=FG_COLOR,
            activeforeground=BG_COLOR,
            relief=tk.SOLID,
            bd=2,
            padx=20,
            pady=10,
            command=_yes,
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            btn_frame,
            text="  No  ",
            font=FONT_BUTTON,
            bg=BG_COLOR,
            fg=FG_COLOR,
            activebackground=FG_COLOR,
            activeforeground=BG_COLOR,
            relief=tk.SOLID,
            bd=2,
            padx=20,
            pady=10,
            command=_no,
        ).pack(side=tk.LEFT, padx=20)

        # Centre dialog on screen after widgets are measured
        dialog.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        dw = dialog.winfo_reqwidth()
        dh = dialog.winfo_reqheight()
        dialog.geometry(f"+{(sw - dw) // 2}+{(sh - dh) // 2}")

        # Make modal: grab all events until the dialog is closed
        dialog.grab_set()
        self.root.wait_window(dialog)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _save_entry(self) -> None:
        """Save the current text as a titled, timestamped .txt file."""
        content = self.text_widget.get("1.0", tk.END).strip()
        if not content:
            self.status_var.set("⚠  Nothing to save — please write something first.")
            return

        # Read title; fall back to "Untitled" when the field is empty
        raw_title = self.title_entry.get().strip()
        display_title = raw_title if raw_title else "Untitled"

        # Sanitise title for use in a filename:
        #   replace spaces with underscores, remove characters that are
        #   unsafe on FAT32 (the Kindle's filesystem).
        _unsafe = r'\/:*?"<>|'
        safe_title = display_title.replace(" ", "_")
        safe_title = "".join(ch for ch in safe_title if ch not in _unsafe)
        if not safe_title:
            safe_title = "Untitled"

        # Ensure the notes directory exists
        try:
            os.makedirs(NOTES_DIR, exist_ok=True)
        except OSError as exc:
            self.status_var.set(f"✗  Cannot create notes folder: {exc}")
            return

        # Build filename: Zetsu_[Title]_[YYYY-MM-DD].txt
        now = datetime.datetime.now()
        filename = f"Zetsu_{safe_title}_{now.strftime('%Y-%m-%d')}.txt"
        filepath = os.path.join(NOTES_DIR, filename)

        # Write the file: title → date/time → separator → body
        try:
            with open(filepath, "w", encoding="utf-8") as note_file:
                note_file.write(f"{display_title}\n")
                note_file.write(f"Date: {now.strftime('%A, %d %B %Y  %H:%M:%S')}\n")
                note_file.write("-" * 40 + "\n\n")
                note_file.write(content + "\n")
        except OSError as exc:
            self.status_var.set(f"✗  Save failed: {exc}")
            return

        self.status_var.set(f"✔  Saved → {filename}")
        # Clear both the title field and the text area after a successful save
        self.title_entry.delete(0, tk.END)
        self.text_widget.delete("1.0", tk.END)

    def _clear_text(self) -> None:
        """Ask for confirmation, then clear the title field and text area."""
        self._ask_confirm("Are you sure?", self._do_clear)

    def _do_clear(self) -> None:
        """Perform the actual clear after the user has confirmed."""
        self.title_entry.delete(0, tk.END)
        self.text_widget.delete("1.0", tk.END)
        self.status_var.set("Text cleared.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    try:
        root = tk.Tk()
        ZetsuDiaryApp(root)
        root.mainloop()
    except Exception as exc:
        import traceback
        print(f"[ZetsuDiary] Fatal GUI error: {exc}", flush=True)
        traceback.print_exc()


if __name__ == "__main__":
    main()
