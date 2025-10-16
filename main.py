# pdf_agent_ui.py
# Simple drag-and-drop PDF UI that sends the file to an (external) agent
# and prints the agent's response in a big label-like text box.
import io, os

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from openai import OpenAI
from system_role import SYSTEM_PROMPT
from system_task import USER_TASK
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    raise SystemExit(
        "Missing dependency: tkinterdnd2\n"
        "Install with:  pip install tkinterdnd2"
    )


USER_TASK = """
Read the attached PDF and produce a structured IRB ML ethics review for the five principles:
Beneficence, Non-Maleficence, Autonomy, Justice, Explicability.

For each principle:
- Quote or summarize the relevant statement(s) from the PDF with exact page numbers.
- Raise 1–3 critical, decision-driving questions per item.
- Where appropriate, add concise comparator notes referencing existing peer-reviewed medical ML papers or recognized guidelines (with DOI/PubMed ID or guideline name & year). If none can be confidently cited, state “Comparative evidence needed”.

Keep it concise, precise, and suitable for expert readers.
"""

def _get_client() -> OpenAI:
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. On Windows run:\n"
            '  setx OPENAI_API_KEY "sk-..."\n'
            "Then close & reopen VS Code/terminal and try again."
        )
    _client = OpenAI(api_key=api_key)
    return _client

def run_agent(pdf_path: str) -> str:
    client = _get_client()

    # Upload PDF
    with open(pdf_path, "rb") as f:
        uploaded = client.files.create(
            file=(os.path.basename(pdf_path), io.BytesIO(f.read()), "application/pdf"),
            purpose="assistants",
        )

    # Ask the model, attach file (no tools needed)
    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "input_text", "text": USER_TASK},
                {"type": "input_file", "file_id": uploaded.id}
            ]}
        ]
    )

    chunks = []
    for item in getattr(resp, "output", []):
        if getattr(item, "type", "") == "message":
            for block in getattr(item, "content", []):
                if getattr(block, "type", "") == "output_text":
                    chunks.append(block.text)
    return "\n".join(chunks).strip() or "(No text received)"


# ---------------------------------------------------------

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF → ChatGPT Agent")
        self.geometry("760x560")
        self.minsize(640, 480)

        # Main container
        container = ttk.Frame(self, padding=14)
        container.pack(fill="both", expand=True)

        # Header
        title = ttk.Label(container, text="Drop a PDF or choose one",
                          font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w", pady=(0, 8))

        # Drop zone
        self.drop_frame = ttk.Frame(container, height=120, style="Drop.TFrame")
        self.drop_frame.pack(fill="x")
        self.drop_frame.pack_propagate(False)

        self.drop_label = ttk.Label(
            self.drop_frame,
            text="⬇️  Drop PDF here",
            anchor="center",
            font=("Segoe UI", 12)
        )
        self.drop_label.pack(expand=True, fill="both", padx=10, pady=10)

        # Enable DnD
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind("<<Drop>>", self._on_drop)

        # Controls
        controls = ttk.Frame(container)
        controls.pack(fill="x", pady=10)

        self.choose_btn = ttk.Button(controls, text="Choose PDF…",
                                     command=self._choose_pdf)
        self.choose_btn.pack(side="left")

        self.status = ttk.Label(controls, text="Ready", anchor="w")
        self.status.pack(side="right")

        # Output box (big ass label box 😉)
        out_label = ttk.Label(container, text="Agent output:",
                              font=("Segoe UI", 10, "bold"))
        out_label.pack(anchor="w", pady=(8, 4))

        self.output = ScrolledText(container, wrap="word", height=16)
        self.output.pack(fill="both", expand=True)
        self.output.configure(font=("Consolas", 10))

        # Styling
        style = ttk.Style(self)
        style.configure("Drop.TFrame", relief="ridge", borderwidth=2)

    # -------------- UI actions --------------
    def _choose_pdf(self):
        path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        if path:
            self._process_pdf(path)

    def _on_drop(self, event):
        # event.data may be a list-like string; take the first path
        raw = event.data.strip()
        # Handle possible braces/quotes from DnD paths
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        path = raw.split()  # if multiple files dropped
        path = path[0]
        if not path.lower().endswith(".pdf"):
            messagebox.showerror("Invalid file", "Please drop a .pdf file.")
            return
        self._process_pdf(path)

    def _process_pdf(self, path: str):
        if not os.path.exists(path):
            messagebox.showerror("Not found", f"File not found:\n{path}")
            return

        self._set_busy(True)
        self._append_output(f"Loading: {path}\n")

        def worker():
            try:
                result = run_agent(path)  # <-- your integration point
            except Exception as e:
                result = f"[ERROR] {e}"
            # Push back to UI thread
            self.after(0, lambda: self._finish(result))

        threading.Thread(target=worker, daemon=True).start()

    def _finish(self, text: str):
        self._append_output("\n" + str(text) + "\n")
        self._set_busy(False)

    def _append_output(self, text: str):
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="normal")  # keep editable if you like

    def _set_busy(self, busy: bool):
        if busy:
            self.status.configure(text="Processing…")
            self.choose_btn.configure(state="disabled")
            self.drop_label.configure(text="Processing…")
        else:
            self.status.configure(text="Ready")
            self.choose_btn.configure(state="normal")
            self.drop_label.configure(text="⬇️  Drop PDF here")


if __name__ == "__main__":
    App().mainloop()


