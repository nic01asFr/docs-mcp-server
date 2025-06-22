# Comment créer la première release

## 1. Finaliser le package

Vérifiez que tout est prêt :
```bash
# Tests locaux
pip install -e ".[dev]"
pytest
ruff check src/ tests/
mypy src/

# Build local
python -m build
twine check dist/*
```

## 2. Créer la release GitHub

1. Aller sur https://github.com/nic01asFr/docs-mcp-server/releases
2. Cliquer "Create a new release"
3. Tag version: `v0.1.0`
4. Release title: `v0.1.0 - Initial Release`
5. Description:
```markdown
## 🎉 Première release du serveur MCP DINUM Docs

### ✨ Fonctionnalités
- 25+ outils MCP pour l'API DINUM Docs
- 4 ressources MCP exposées
- Client HTTP complet avec gestion d'erreurs
- CLI professionnel avec vérification config
- Support Docker

### 📦 Installation
```bash
pip install docs-mcp-server
```

### 🔧 Configuration
Voir la documentation: https://github.com/nic01asFr/docs-mcp-server#readme
```

6. Publier la release → Le workflow publiera automatiquement sur PyPI

## 3. Vérification post-release

Une fois publié, testez :
```bash
pip install docs-mcp-server
docs-mcp-server --version
docs-mcp-server --config-check
```
