# 🛡️ PyIA — Assistant Pentest IA

> Interface graphique combinant terminal, cartographie réseau, profils Nmap et chat IA.
> Conçu pour Kali Linux.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Kali](https://img.shields.io/badge/Kali_Linux-557C94?logo=kalilinux&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Fonctionnalités

- **🖥️ Terminal intégré** — Bash avec coloration syntaxique, historique, exécution async
- **🗺️ Cartographie réseau** — Graphe auto depuis scans Nmap, détection OS, import XML
- **📋 Profils Nmap** — Profils prédéfinis + personnalisés, lancement en un clic
- **🤖 Chat IA** — Ollama (local), OpenAI, Anthropic
- **🎨 3 thèmes** — Sombre, Clair, Cyberpunk
- **💾 Projets** — Sauvegarde/chargement JSON

---

## 🚀 Installation

```bash
# Dépendances système
sudo apt install python3-tk nmap

# Clone + install
git clone https://github.com/VOTRE_USERNAME/pyia.git
cd pyia
pip install matplotlib networkx requests

# Lancer
sudo python3 gpt32.py

📖 Utilisation rapide

    Terminal → tapez nmap -sV 192.168.1.0/24 → les hôtes apparaissent dans le graphe
    Profils → sélectionnez un profil, entrez la cible, cliquez ▶ Lancer
    Import → Fichier → Importer XML Nmap
    Chat IA → configurez Ollama/OpenAI/Anthropic, posez vos questions


⚙️ Configuration IA
Ollama (Local — Recommandé)

# Installer Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Télécharger un modèle
ollama pull llama3.1
ollama pull mistral

# Ollama tourne sur http://localhost:11434
# PyIA le détecte automatiquement

OpenAI

    Obtenez une clé API sur platform.openai.com
    Dans PyIA → Chat IA → Provider : openai
    Entrez votre clé API
    Modèle recommandé : gpt-4 ou gpt-3.5-turbo

Anthropic

    Obtenez une clé API sur console.anthropic.com
    Dans PyIA → Chat IA → Provider : anthropic
    Entrez votre clé API
    Modèle recommandé : claude-3-sonnet-20240229


⚠️ Avertissement

Usage légal uniquement. Utilisez cet outil exclusivement sur des systèmes pour lesquels vous avez une autorisation explicite. L'auteur décline toute responsabilité en cas d'utilisation abusive.
