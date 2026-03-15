# OpenClaw Skills Kit

Skills et templates pour créer et gérer des agents IA avec [OpenClaw](https://github.com/openclaw/openclaw) (>= 2026.3.8).

## Contenu

### `/commands/agent-openclaw.md`
Commande interactive pour créer un agent OpenClaw de A à Z en 6 phases :
- **Phase 0** : Installation (Node.js, Bun, OpenClaw)
- **Phase 1** : Choix du template (Polyvalent, Commercial, SAV, Assistant)
- **Phase 2** : Identité de l'agent (IDENTITY.md, USER.md, SOUL.md)
- **Phase 3** : Configuration (modèle, mémoire, CRM, canal)
- **Phase 4** : Équipement du workspace
- **Phase 5** : Déploiement + tests + GO/NO-GO
- **Phase 6** : Maintenance et mises à jour

Inclut un **avocat du diable** (objections concrètes aux phases 2-4) et un **superviseur** (checklist GO/NO-GO en phase 5).

### `/skills/maj-openclaw/`
Skill de vérification des mises à jour OpenClaw : version, changelog, bugs GitHub, santé gateway, verdict (mettre à jour / attendre).

### `/templates/agent-openclaw/`
Templates réutilisables pour les agents :
- `souls/` : 4 profils (polyvalent, commercial, SAV, assistant personnel)
- `scripts/` : CRM local (Python), email (SMTP/IMAP), healthcheck
- `guide-proprietaire.md` : manuel utilisateur en 6 gestes
- `crm-template.md` : structure du CRM (champs, scoring BANT, workflow)

## Installation

Copier les fichiers dans votre configuration Claude Code :

```bash
# Commande
cp commands/agent-openclaw.md ~/.claude/commands/

# Skill
cp -r skills/maj-openclaw ~/.claude/skills/

# Templates
cp -r templates/agent-openclaw ~/.claude/templates/
```

Puis lancer `/agent-openclaw Mon premier agent` dans Claude Code.

## Autres CLI IA (Codex, Gemini CLI)

Les templates et scripts fonctionnent tels quels avec n'importe quel assistant IA. Pour le skill `agent-openclaw.md`, copiez son contenu dans votre fichier d'instructions (`AGENTS.md` pour Codex, `GEMINI.md` pour Gemini CLI) ou collez-le en prompt. Le frontmatter `---` en tête de fichier est spécifique à Claude Code et peut être ignoré.

## Prérequis

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) ou équivalent
- [OpenClaw](https://github.com/openclaw/openclaw) >= 2026.3.8
- Node.js >= 22
- Un provider LLM (ChatGPT Plus, Anthropic, Infomaniak AI, Ollama)

## Compatibilité

Testé avec OpenClaw 2026.3.8 à 2026.3.13 sur Ubuntu 22.04/24.04 et macOS.

## Licence

MIT
