---
name: maj-openclaw
description: Vérifie les MAJ OpenClaw, analyse changelog + bugs GitHub, donne un verdict
user_invocable: true
---

# Skill /maj-openclaw - Vérification MAJ OpenClaw

Analyse complète de la situation OpenClaw : version, changelog, bugs, santé gateway, verdict.

## Étapes

### 1. Versions (en parallèle)

Lancer en parallèle sur chaque machine :
- `openclaw --version` → version installée
- `npm view openclaw version` → version npm disponible

Si les deux sont identiques : le dire et proposer quand même l'analyse des bugs ouverts.

### 2. Changelog

Si MAJ disponible :
- `WebFetch` sur `https://github.com/openclaw/openclaw/releases` → extraire le changelog de la nouvelle version vs l'actuelle
- Résumer les **breaking changes**, **bugfixes**, et **nouvelles fonctionnalités**
- Évaluer l'impact pour la config : canaux actifs (Discord, WhatsApp, Telegram), subagents, cron jobs

### 3. Bugs ouverts GitHub

Lancer en parallèle :
- `gh issue list --repo openclaw/openclaw --state open --label bug --limit 20` → bugs taggés
- `gh issue list --repo openclaw/openclaw --state open --limit 50` → tous les issues récents

Filtrer les bugs **pertinents pour l'infra** :
- Discord (typing, event lane, images, attachments)
- WhatsApp (group messages, multi-account)
- Tool calls (perte, crash, normalisation)
- Compaction / mémoire / timestamps
- Workspace / cwd / sessions
- Subagents / delivery
- Cron / heartbeat

Pour chaque bug pertinent : `gh issue view <numéro> --repo openclaw/openclaw` pour lire le détail.

### 4. Santé gateway

Lancer en parallèle sur chaque machine :
- `systemctl --user status openclaw-gateway` → statut service
- `ps aux | grep openclaw-gateway | grep -v grep` → process actifs
- `journalctl --user -u openclaw-gateway -n 50 --no-pager | grep -i -E 'error|warn|fail'` → erreurs récentes

Signaler :
- Process zombies (plusieurs gateway)
- Erreurs de lock
- Crashes récents
- Tentatives de restart échouées

### 5. Conversations agents (optionnel)

Si demandé ou si bugs suspectés :
- Regarder les sessions récentes des agents pour des erreurs
- `ls -lt ~/.openclaw/agents/[agent-id]/sessions/*.jsonl | head -5`
- Chercher : `error`, `fail`, `crash`, `timeout`, `denied` dans les sessions

### 6. Verdict

Présenter un tableau récapitulatif :

```
## Verdict MAJ

| Critère | Résultat |
|---------|----------|
| Version actuelle | X.Y.Z |
| Version disponible | X.Y.Z |
| Breaking changes | oui/non (détails) |
| Bugs bloquants dans la nouvelle version | oui/non (lesquels) |
| Fixes pertinents | liste |
| Santé gateway | OK/problèmes |
| **Recommandation** | **Mettre à jour / Attendre** |
```

Si recommandation = mettre à jour, rappeler la procédure :
```bash
openclaw gateway stop
lsof -ti :18789 | xargs kill -9 2>/dev/null  # tuer zombies
npm install -g openclaw@latest
openclaw doctor --fix
openclaw gateway install --force  # réinstalle le service systemd
openclaw gateway start
openclaw --version  # vérifier
```

Si recommandation = attendre, préciser quel bug/fix surveiller pour déclencher la MAJ.

## Infos de référence

- **Service systemd** : `openclaw-gateway` (user-level)
- **Config** : `~/.openclaw/openclaw.json`
- **State dir** : `~/.openclaw/`
- **Agents** : `~/.openclaw/agents/[id]/`
- **GitHub repo** : `openclaw/openclaw`
