# Guide d'Installation Claude Desktop

Ce guide explique comment installer et configurer le serveur MCP DINUM Docs avec Claude Desktop.

## 📋 Prérequis

- Claude Desktop installé
- Python 3.8+ 
- Accès à une instance DINUM Docs
- Token d'API DINUM Docs

## 🚀 Installation

### Étape 1 : Installer le package

```bash
# Via PyPI (après release)
pip install docs-mcp-server

# Ou depuis le code source
git clone https://github.com/nic01asFr/docs-mcp-server.git
cd docs-mcp-server
pip install -e .
```

### Étape 2 : Vérifier l'installation

```bash
docs-mcp-server --version
# Output: docs-mcp-server 0.1.0
```

### Étape 3 : Configurer les variables d'environnement

```bash
# Linux/macOS
export DOCS_BASE_URL="https://votre-instance-docs.gouv.fr"
export DOCS_API_TOKEN="votre-token-api"

# Windows
set DOCS_BASE_URL=https://votre-instance-docs.gouv.fr
set DOCS_API_TOKEN=votre-token-api
```

### Étape 4 : Tester la configuration

```bash
docs-mcp-server --config-check
```

Sortie attendue :
```
✓ Configuration loaded successfully
  Base URL: https://votre-instance-docs.gouv.fr
  Token: ****-api-****-1234
  Timeout: 30s
  Max retries: 3
✓ API connection successful
  Authenticated as: votre.email@ministere.gouv.fr
  User ID: user-123
```

## ⚙️ Configuration Claude Desktop

### Étape 5 : Localiser le fichier de configuration

Le fichier de configuration Claude Desktop se trouve à :

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Étape 6 : Modifier la configuration

Ajoutez la configuration MCP au fichier `claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "docs-mcp-server": {
      "command": "docs-mcp-server",
      "args": [],
      "env": {
        "DOCS_BASE_URL": "https://votre-instance-docs.gouv.fr",
        "DOCS_API_TOKEN": "votre-token-api"
      }
    }
  }
}
```

### Étape 7 : Configuration avancée (optionnel)

Pour une configuration plus robuste avec options personnalisées :

```json
{
  "mcpServers": {
    "docs-mcp-server": {
      "command": "docs-mcp-server",
      "args": [
        "--name", "mon-serveur-docs",
        "--verbose"
      ],
      "env": {
        "DOCS_BASE_URL": "https://votre-instance-docs.gouv.fr",
        "DOCS_API_TOKEN": "votre-token-api",
        "DOCS_TIMEOUT": "60",
        "DOCS_MAX_RETRIES": "5"
      }
    }
  }
}
```

### Étape 8 : Redémarrer Claude Desktop

1. Fermer complètement Claude Desktop
2. Relancer l'application
3. Vérifier que le serveur MCP est connecté

## 🔧 Utilisation dans Claude

Une fois configuré, vous pouvez utiliser les outils dans Claude :

### Exemples de commandes

```
# Lister les documents
Peux-tu me montrer mes documents récents ?

# Créer un document
Crée un nouveau document intitulé "Rapport mensuel" avec un plan de base

# Rechercher des documents
Trouve tous les documents contenant "budget" dans le titre

# Partager un document
Donne accès en lecture à jean.dupont@ministere.gouv.fr sur le document "Plan stratégique"

# Utiliser l'IA pour améliorer du texte
Corrige et améliore ce texte : "Voici un brouillon de rapport..."
```

### Outils disponibles

Le serveur expose 25+ outils MCP :

**Gestion de documents :**
- `docs_list_documents` - Lister les documents
- `docs_get_document` - Récupérer un document
- `docs_create_document` - Créer un document  
- `docs_update_document` - Modifier un document
- `docs_delete_document` - Supprimer un document

**Gestion des accès :**
- `docs_grant_access` - Donner accès à un utilisateur
- `docs_list_accesses` - Lister les permissions
- `docs_invite_user` - Inviter un utilisateur

**Fonctionnalités IA :**
- `docs_ai_transform` - Transformer du texte (corriger, résumer, etc.)
- `docs_ai_translate` - Traduire du texte

**Et bien plus...**

## 🐛 Dépannage

### Problèmes courants

**1. Serveur MCP non détecté**
```bash
# Vérifier l'installation
which docs-mcp-server
docs-mcp-server --version
```

**2. Erreur d'authentification**
```bash
# Tester la configuration
docs-mcp-server --config-check
```

**3. Timeout de connexion**
```json
{
  "env": {
    "DOCS_TIMEOUT": "120"
  }
}
```

**4. Problèmes de certificats SSL**
Pour les instances avec certificats auto-signés, contactez votre administrateur système.

### Logs de débogage

Pour activer les logs détaillés :

```json
{
  "mcpServers": {
    "docs-mcp-server": {
      "command": "docs-mcp-server",
      "args": ["--verbose"],
      "env": { ... }
    }
  }
}
```

## 🔄 Mise à jour

```bash
# Mettre à jour vers la dernière version
pip install --upgrade docs-mcp-server

# Redémarrer Claude Desktop après mise à jour
```

## 📞 Support

- **Documentation :** https://github.com/nic01asFr/docs-mcp-server
- **Issues :** https://github.com/nic01asFr/docs-mcp-server/issues
- **Discussions :** https://github.com/nic01asFr/docs-mcp-server/discussions

## 🏢 Configuration en entreprise

Pour un déploiement en entreprise, consultez la documentation avancée :
- Configuration centralisée
- Gestion des secrets
- Monitoring et observabilité
- Déploiement Docker
