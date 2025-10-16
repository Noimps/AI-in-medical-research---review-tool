# PDF → ChatGPT Agent (IRB ML ethics reviewer)

Small desktop tool that lets you drop or choose a PDF and sends it to an OpenAI ChatGPT-based agent which returns a structured IRB-style ML ethics review. Intended use specifically for medical research that proposes usage of an AI framework.

## What this tool does
- Opens a simple Tkinter GUI where you can drag & drop a PDF or choose one with a file dialog.
- Uploads the PDF to the OpenAI Responses API and sends two prompt components:
  - The system role prompt (instructions for the reviewer)
  - The user task prompt (what to do with the attached PDF)
- Displays the model's textual reply in a large scrollable text area.

The project uses OpenAI's ChatGPT (Responses API) — by default the code requests the `gpt-4.1-mini` model.

## Files of interest
- `main.py` — the GUI and integration code; this is the program you run.
- `system_role.py` — contains the long system prompt (the IRB ML ethics reviewer role). Edit this file to change the system role wording.
- `system_task.py` — contains the user task prompt (the task instructions for the model). Edit this file to change the user-facing task.

Both `system_role.py` and `system_task.py` are simple Python modules that define the prompt strings `SYSTEM_PROMPT` and `USER_TASK`. Modifying those files will change what the model is instructed to do.

## Dependencies
Install the required Python packages (example):

```powershell
pip install openai tkinterdnd2
```

Notes:
- `tkinterdnd2` is required for drag-and-drop support. If it's not present the program exits with an error telling you how to install it.
- The project imports `OpenAI` from the official OpenAI Python package.

## Setting the OpenAI API key (Windows PowerShell)
The code reads the API key from the environment variable `OPENAI_API_KEY`:

```python
api_key = os.getenv("OPENAI_API_KEY")
```

Recommended ways to set the key on Windows:

1) Persist across sessions (user-level, recommended):

```powershell
setx OPENAI_API_KEY "sk-..."
```

After running `setx` you must close and re-open PowerShell and restart VS Code (or any GUI) so new processes see the variable.

2) For the current PowerShell session only (temporary, useful for testing):

```powershell
$env:OPENAI_API_KEY = "sk-..."
python main.py
```

3) To check whether the variable is visible in the current PowerShell session (safe, masked):

```powershell
if ($env:OPENAI_API_KEY) { $env:OPENAI_API_KEY.Substring(0,4) + "..." + $env:OPENAI_API_KEY.Substring($env:OPENAI_API_KEY.Length - 4) } else { "OPENAI_API_KEY not set" }
```

4) Remove a persistent user-level variable:

```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $null, "User")
```

Security note: Do not commit your API key to source control. Avoid pasting the full key into shared chats or screenshots.

## How to run

1. Ensure dependencies are installed (see Dependencies above).
2. Set `OPENAI_API_KEY` as shown.
3. From this project directory run:

```powershell
python main.py
```

The GUI will open. Drop or choose a PDF to send it to the model. Results appear in the output box.

## OpenAI API key help
To create an API key or learn about OpenAI authentication, see OpenAI's docs:

https://platform.openai.com/account/api-keys

or the authentication guide:

https://platform.openai.com/docs/guides/authentication

## Model / behavior notes
- The code currently uses the Responses API and requests model `gpt-4.1-mini`. This is a ChatGPT-family model — you can change the model string in `main.py` if you want to try other available models.
- The system role and user task prompts live in `system_role.py` and `system_task.py`. Keep prompt lengths and guardrails in mind when editing — the model's output will follow those instructions.

## Troubleshooting
- If the program exits with a message about `tkinterdnd2`, install it with `pip install tkinterdnd2`.
- If you get a runtime error that `OPENAI_API_KEY is not set`, confirm you set the environment variable in a shell that has been restarted after `setx`, or set it temporarily with `$env:OPENAI_API_KEY`.
- If responses are empty, check console output for errors and verify the uploaded file is a valid PDF.

## Quick development tips
- Prefer editing `system_role.py` / `system_task.py` rather than hard-coding prompts in `main.py`.
- For secret management in development consider using a `.env` + `python-dotenv` (do not commit the `.env` file), or a secret manager for production.

## License & safety
This project includes no license text by default — add one if you intend to release it. Treat model outputs as advisory only and do not rely on them for clinical or legal decisions.

---

