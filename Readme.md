# 🛡️ PyIA — Assistant Pentest IA avec Interface Graphique

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Tkinter-GUI-green?logo=linux&logoColor=white" alt="Tkinter">
  <img src="https://img.shields.io/badge/Nmap-Integration-orange?logo=nmap&logoColor=white" alt="Nmap">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
  <img src="https://img.shields.io/badge/Platform-Kali%20Linux-557C94?logo=kalilinux&logoColor=white" alt="Kali">
</p>

<p align="center">
  <b>Un assistant de pentest intelligent combinant terminal intégré, cartographie réseau automatique,<br>
  gestion de profils Nmap et chat IA — le tout dans une interface graphique moderne.</b>
</p>

---

## 📸 Aperçu

┌─────────────────────────────────────────────────────────────────┐
│  PyIA — Pentest AI Assistant                                    │
├──────────┬──────────────┬───────────────────┬───────────────────┤
│ Terminal │ Graphique    │ Éditeur Profils   │ Chat IA           │
│ Intégré  │ Réseau       │ Nmap              │                   │
│          │              │                   │                   │
│ $> nmap  │  ┌───┐       │ Profil: Quick     │ 🤖 Comment puis- │
│   -sV    │  │ H1├──┐    │ Args: -sV -T4    │    je vous aider? │
│ 10.0.0.1 │  └───┘  │    │                   │                   │
│          │     ┌────┴┐   │ [Lancer] [Sauver] │ > Analyse cette  │
│ PORT     │     │ H2  │   │                   │   sortie nmap    │
│ 22/tcp   │     └─────┘   │                   │                   │
│ 80/tcp   │              │                   │ 🤖 Je détecte 2  │
│ 443/tcp  │              │                   │   services...     │
└──────────┴──────────────┴───────────────────┴───────────────────┘


---

## ✨ Fonctionnalités

### 🖥️ Terminal Intégré
- Terminal bash complet directement dans l'interface
- Coloration syntaxique (IPs, commandes, user@host)
- Historique des commandes (↑ / ↓)
- Détection automatique des commandes `nmap` avec parsing des résultats
- Exécution asynchrone (l'interface reste réactive)

### 🗺️ Cartographie Réseau Automatique
- Graphique interactif généré automatiquement depuis les scans Nmap
- Visualisation des hôtes avec identification OS (icônes Linux/Windows)
- Détection des réseaux et regroupement par sous-réseau
- Affichage détaillé : ports ouverts, services, versions
- Clic sur un hôte → détails complets + notes personnalisées
- Import de fichiers XML Nmap existants

### 📋 Éditeur de Profils Nmap
- Profils prédéfinis : Quick Scan, Full TCP, UDP, Vulners, Stealth…
- Création / modification / suppression de profils personnalisés
- Sélection de cible + lancement en un clic
- Résultats intégrés directement dans la cartographie

### 🤖 Chat IA
- Interface de conversation intégrée
- Support multi-providers (Ollama local, OpenAI, Anthropic)
- Configuration clé API et modèle dans l'interface
- Contexte pentest : posez des questions sur vos résultats de scan
- Réponses formatées avec coloration

### 🎨 Interface Moderne
- 3 thèmes : **Sombre**, **Clair**, **Cyberpunk**
- Changement de thème en temps réel
- Interface responsive avec panneaux redimensionnables
- Barre de menu complète (Fichier, Thème, Aide)

### 💾 Gestion de Projet
- Sauvegarde complète du projet (hôtes, réseaux, notes, profils)
- Chargement de projets existants
- Format JSON lisible et portable
- Export des données de cartographie

---

## 🚀 Installation

### Prérequis

- **Python 3.10+**
- **Tkinter** (inclus dans la plupart des distributions Python)
- **Nmap** installé sur le système
- **Kali Linux** recommandé (mais fonctionne sur toute distribution Linux)

### Installation rapide

```bash
# Cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/pyia.git
cd pyia

# Installer les dépendances Python
pip install -r requirements.txt

# Lancer l'application
python pyia.py

Dépendances

# Dépendances système
sudo apt update
sudo apt install python3-tk nmap

# Dépendances Python
pip install matplotlib networkx requests

Fichier requirements.txt

matplotlib>=3.7
networkx>=3.0
requests>=2.28


📖 Utilisation
Lancement

# Lancement standard
python gpt32.py

# Avec droits root (nécessaire pour certains scans Nmap)
sudo python gpt32.py

Terminal Intégré

# Tapez directement vos commandes dans le terminal intégré
nmap -sV -T4 192.168.1.0/24

# Les résultats Nmap sont automatiquement parsés
# et les hôtes apparaissent dans la cartographie réseau

Profils Nmap

    Allez dans l'onglet Éditeur Profils
    Sélectionnez un profil prédéfini ou créez le vôtre
    Entrez l'IP / plage cible
    Cliquez sur ▶ Lancer le scan
    Les résultats apparaissent automatiquement dans Graphique Réseau

Import XML Nmap

# Réalisez un scan avec sortie XML
nmap -sV -oX scan_results.xml 192.168.1.0/24

Puis : Fichier → 📥 Importer XML Nmap et sélectionnez le fichier.
Chat IA

    Allez dans l'onglet Chat IA
    Configurez votre provider :
        Ollama (local) : http://localhost:11434 — aucune clé nécessaire
        OpenAI : entrez votre clé API
        Anthropic : entrez votre clé API
    Posez vos questions sur les résultats de scan ou demandez des conseils

Sauvegarde / Chargement

    Fichier → 💾 Sauvegarder projet : exporte tout en JSON
    Fichier → 📂 Charger projet : restaure un projet complet

🗂️ Structure du Projet

pyia/
├── gpt32.py              # Application principale (tout-en-un)
├── requirements.txt      # Dépendances Python
├── README.md             # Ce fichier
├── LICENSE               # Licence MIT
└── screenshots/          # Captures d'écran (optionnel)
    ├── terminal.png
    ├── network_graph.png
    ├── profiles.png
    └── chat_ai.png

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

🎨 Thèmes
Thème 	Description
🌙 Sombre 	Thème par défaut, fond noir, idéal pour le travail nocturne
☀️ Clair 	Fond blanc classique, haute lisibilité
💜 Cyberpunk 	Violet néon, style futuriste hacker

Changez de thème via Thème dans la barre de menu.
🔒 Avertissement Légal

    ⚠️ Cet outil est destiné UNIQUEMENT à des fins éducatives et à des tests de sécurité autorisés.

    L'utilisation de cet outil contre des systèmes sans autorisation explicite est illégale.
    L'auteur décline toute responsabilité en cas d'utilisation abusive.

    Respectez toujours :

        Les lois locales et internationales
        Les règles d'engagement définies
        Le périmètre d'audit autorisé
        L'éthique professionnelle en cybersécurité


Idées futures

    Support de nouveaux outils (Masscan, Nikto, Gobuster…)
    Export rapport PDF/HTML
    Base de données SQLite pour les projets
    Détection automatique de vulnérabilités
    Intégration Metasploit
    Mode collaboration multi-utilisateurs
    Plugin system
    Support Windows / macOS natif

📝 Changelog
v1.0.0 — Version initiale

    ✅ Terminal intégré avec coloration syntaxique
    ✅ Cartographie réseau automatique (Nmap)
    ✅ Éditeur de profils Nmap
    ✅ Chat IA multi-providers
    ✅ 3 thèmes (Sombre, Clair, Cyberpunk)
    ✅ Sauvegarde/Chargement de projets JSON
    ✅ Import XML Nmap


<p align="center"> <b>Fait avec ❤️ pour la communauté cybersécurité</b><br> <i>⭐ Star ce projet si vous le trouvez utile !</i> </p> ``` 
