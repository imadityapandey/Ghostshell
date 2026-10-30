# 👻 GhostShell

Local AI terminal companion. Runs 100% on your machine.

## Setup
pip install -r requirements.txt
ollama pull gemma:2b

## Usage
python ghostshell.py explain "find . -name '*.log' -delete"
python ghostshell.py diagnose error.log
python ghostshell.py safety "rm -rf /"
python ghostshell.py chat