#!/usr/bin/env python3
"""
Unfolder GUI - Simple desktop front-end for unfolder.py

Lets a user pick a folder, choose options, and extract nested archives
without touching a terminal or PowerShell. Just double-click and go.

Requires: unfolder.py in the same folder (imported directly below).
"""

import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path

# unfolder.py must live next to this file
sys.path.insert(0, str(Path(__file__).parent))
from unfolder import SimpleExtractor, preview_extraction


class TextRedirector:
    """Redirects print() output into a Tkinter text widget, thread-safe."""

    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        # Marshal back onto the Tk main thread
        self.widget.after(0, self._append, text)

    def _append(self, text):
        self.widget.configure(state="normal")
        self.widget.insert("end", text)
        self.widget.see("end")
        self.widget.configure(state="disabled")

    def flush(self):
        pass


class UnfolderApp:
    def __init__(self, root):
        self.root = root
        root.title("Unfolder - Archive Extractor")
        root.geometry("640x480")
        root.minsize(560, 420)

        self.folder_var = tk.StringVar()
        self.delete_var = tk.BooleanVar(value=False)
        self.flat_var = tk.BooleanVar(value=False)
        self.busy = False

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        top = tk.Frame(self.root)
        top.pack(fill="x", **pad)
        tk.Label(top, text="Folder to scan:").pack(side="left")
        tk.Entry(top, textvariable=self.folder_var).pack(
            side="left", fill="x", expand=True, padx=8
        )
        tk.Button(top, text="Browse...", command=self.browse_folder).pack(side="left")

        opts = tk.Frame(self.root)
        opts.pack(fill="x", **pad)
        tk.Checkbutton(
            opts, text="Delete archives after successful extraction",
            variable=self.delete_var,
        ).pack(side="left")
        tk.Checkbutton(
            opts, text="Flat mode (siblings instead of nested)",
            variable=self.flat_var,
        ).pack(side="left", padx=20)

        btns = tk.Frame(self.root)
        btns.pack(fill="x", **pad)
        self.preview_btn = tk.Button(
            btns, text="Preview (dry run)", command=self.run_preview
        )
        self.preview_btn.pack(side="left")
        self.extract_btn = tk.Button(
            btns, text="Extract", command=self.run_extract, bg="#2e7d32", fg="white"
        )
        self.extract_btn.pack(side="left", padx=10)

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(self.root, textvariable=self.status_var, anchor="w").pack(
            fill="x", padx=10
        )

        self.log = scrolledtext.ScrolledText(
            self.root, state="disabled", wrap="word",
            bg="#111111", fg="#dddddd", font=("Consolas", 9),
        )
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def browse_folder(self):
        folder = filedialog.askdirectory(
            title="Select folder containing your archive files"
        )
        if folder:
            self.folder_var.set(folder)

    def _get_folder(self):
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showwarning("No folder selected", "Please choose a folder first.")
            return None
        if not Path(folder).exists():
            messagebox.showerror("Folder not found", f"'{folder}' does not exist.")
            return None
        return folder

    def _set_busy(self, busy, status):
        self.busy = busy
        self.status_var.set(status)
        state = "disabled" if busy else "normal"
        self.preview_btn.configure(state=state)
        self.extract_btn.configure(state=state)

    def _clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def run_preview(self):
        if self.busy:
            return
        folder = self._get_folder()
        if not folder:
            return
        self._clear_log()
        self._set_busy(True, "Scanning for archives...")
        threading.Thread(target=self._preview_worker, args=(folder,), daemon=True).start()

    def _preview_worker(self, folder):
        old_stdout = sys.stdout
        sys.stdout = TextRedirector(self.log)
        try:
            preview_extraction(folder)
        except Exception as e:
            print(f"\nPreview failed: {e}")
        finally:
            sys.stdout = old_stdout
            self.root.after(0, self._set_busy, False, "Preview complete.")

    def run_extract(self):
        if self.busy:
            return
        folder = self._get_folder()
        if not folder:
            return
        if not messagebox.askyesno(
            "Confirm extraction",
            "Extract all nested archives in:\n\n"
            f"{folder}\n\n"
            f"Delete originals after: {'Yes' if self.delete_var.get() else 'No'}\n"
            f"Mode: {'Flat' if self.flat_var.get() else 'Nested (in-place)'}\n\n"
            "Continue?",
        ):
            return
        self._clear_log()
        self._set_busy(True, "Extracting...")
        threading.Thread(target=self._extract_worker, args=(folder,), daemon=True).start()

    def _extract_worker(self, folder):
        old_stdout = sys.stdout
        sys.stdout = TextRedirector(self.log)
        try:
            extractor = SimpleExtractor(
                folder,
                delete_after=self.delete_var.get(),
                maintain_hierarchy=not self.flat_var.get(),
            )
            extractor.extract_all()
        except Exception as e:
            print(f"\nExtraction failed: {e}")
        finally:
            sys.stdout = old_stdout
            self.root.after(0, self._set_busy, False, "Done.")


def main():
    root = tk.Tk()
    UnfolderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
