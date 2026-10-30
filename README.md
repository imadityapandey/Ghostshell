# 👻 GhostShell

**Your 100% Local, Privacy-First AI Terminal Companion.**

[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-2026-orange.svg)](https://hacktoberfest.com/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

GhostShell is a Command Line Interface (CLI) tool that brings the power of AI directly into your terminal. Unlike cloud-based AI tools (like ChatGPT), GhostShell uses **Ollama** and open-weight models (like Gemma) to run **entirely on your local machine**. This means you get instant, intelligent help without any data ever leaving your computer.

## ✨ Why GhostShell?
*   🔒 **Privacy-First:** Your code, error logs, and commands never touch the internet.
*   ⚡ **Zero Latency:** No waiting for API responses. It runs directly on your CPU/GPU.
*   💸 **Zero Cost:** No API keys, no monthly subscriptions, no token limits.
*   ✈️ **Offline Capable:** Works perfectly even when you have no internet connection.

## 🚀 Features
*   🧠 **Explain:** Translates complex, intimidating shell commands into plain English.
*   🩺 **Diagnose:** Reads massive, overwhelming error logs and provides a clear 3-step solution.
*   🛡️ **Safety Scan:** Uses built-in Regex patterns to warn you *before* you run dangerous commands (e.g., `rm -rf /` or fork bombs).
*   💬 **Interactive Chat:** A built-in local chat mode to quickly ask coding questions without breaking your workflow.


## 🛠️ Prerequisites
Before you begin, ensure you have the following installed:
1.  **Python 3.9+**
2.  **Ollama:** Download and install from [ollama.com](https://ollama.com/).
3.  **Gemma 2B Model:** Once Ollama is installed, run this in your terminal:
    ```bash
    ollama pull gemma:2b
