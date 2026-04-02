# Linux-command-simulator 🖥️

> Practice Linux commands in the browser. No VM, no risk, no setup.

A virtual Linux terminal running in Flask with an in-memory filesystem. Good for getting comfortable with the command line without touching a real system.

## Supported commands

`pwd` · `ls` (`-l`, `-a`, `-la`) · `cd` · `mkdir` · `nano` · `chmod` · `base64` · `ps`

Also has `ll`, `la`, `l` aliases and simulated env vars (`USER`, `HOME`, `SHELL`, `PATH`).

## Run

```bash
git clone https://github.com/Dreadonyx/Linux-command-simulator
cd Linux-command-simulator
pip install flask
python app.py
```

Open `http://localhost:5000`.

## Stack

- Python / Flask
- In-memory virtual filesystem
- Vanilla JS terminal UI
