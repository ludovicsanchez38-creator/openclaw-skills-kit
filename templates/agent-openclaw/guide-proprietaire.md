# Guide Propriétaire - [Nom de l'agent]

> Les gestes essentiels pour piloter votre agent au quotidien.

## 1. Modifier une offre ou un tarif

```bash
# Rendre le fichier modifiable
chmod 644 /opt/clawdbot/workspace-[id]/TOOLS.md

# Modifier le fichier (avec nano, ou demander à votre assistant IA)
nano /opt/clawdbot/workspace-[id]/TOOLS.md

# Remettre en lecture seule
chmod 444 /opt/clawdbot/workspace-[id]/TOOLS.md

# Redémarrer pour prendre en compte
openclaw gateway stop && openclaw gateway start
```

Pour modifier le comportement de l'agent (ton, règles, flow) : même procédure sur `SOUL.md`.

**Alternative sans terminal** : envoyez un message à votre agent en mode propriétaire (depuis votre numéro autorisé) : "Modifie le prix de [offre] à [nouveau prix]". Si l'agent a les droits `elevated`, il peut modifier ses propres fichiers.

## 2. Consulter le CRM

```bash
# Chercher un contact
python3 /opt/clawdbot/workspace-[id]/scripts/crm-local.py '{"command":"lookup","args":{"phone":"+33612345678"}}'

# Voir les relances du jour
python3 /opt/clawdbot/workspace-[id]/scripts/crm-local.py '{"command":"list_relances","args":{}}'

# Voir les tickets SAV d'un client
python3 /opt/clawdbot/workspace-[id]/scripts/crm-local.py '{"command":"sav_list","args":{"phone":"+33612345678"}}'

# Lister tous les tickets SAV ouverts
python3 /opt/clawdbot/workspace-[id]/scripts/crm-local.py '{"command":"sav_list_open","args":{}}'

# Ajouter un contact manuellement
python3 /opt/clawdbot/workspace-[id]/scripts/crm-local.py '{"command":"create","args":{"phone":"+33612345678","prenom":"Marie","source":"manuel"}}'
```

## 3. Lire les logs

```bash
# Logs en temps réel (Ctrl+C pour arrêter)
openclaw logs -f

# Logs de la dernière heure
journalctl --user -u openclaw-gateway --since "1 hour ago"

# Logs du healthcheck
cat /tmp/openclaw-heartbeat.log
```

**Erreurs courantes** :
- `ECONNREFUSED` : la gateway ne tourne pas → redémarrer (geste 4)
- `401 Unauthorized` : token canal expiré → relancer `openclaw whatsapp link`
- `QMD timeout` : mémoire surchargée → `openclaw memory index --force`
- `session limit reached` : trop de conversations → redémarrer (elles seront purgées)

## 4. Redémarrer l'agent

```bash
# Redémarrage propre
openclaw gateway stop && openclaw gateway start

# Vérifier que tout tourne
openclaw agents list
openclaw memory status --deep
```

Si le redémarrage ne fonctionne pas :
```bash
# Forcer l'arrêt puis relancer
lsof -ti :18789 | xargs kill -9 2>/dev/null
openclaw gateway start
```

## 5. Vérifier la mémoire

```bash
# Statut de la mémoire
openclaw memory status --deep

# Si "not ready" : forcer la réindexation
openclaw memory index --force
```

La mémoire se distille automatiquement. Tous les 15 jours, archivez les vieux fichiers :
```bash
ls /opt/clawdbot/workspace-[id]/memory/
# Déplacer les fichiers de plus de 14 jours dans archive/
```

## 6. Modifier les relances automatiques

Les délais de relance (J+2, J+7, J+14) sont définis dans `AGENTS.md` :
```bash
chmod 644 /opt/clawdbot/workspace-[id]/AGENTS.md
nano /opt/clawdbot/workspace-[id]/AGENTS.md
# Chercher la section "relances" et modifier les délais
chmod 444 /opt/clawdbot/workspace-[id]/AGENTS.md
openclaw gateway stop && openclaw gateway start
```

---

## Les 10 premiers jours

| Jour | Action |
|------|--------|
| 1-2 | Observer les conversations, ne pas toucher au SOUL.md |
| 3 | Premier ajustement si besoin (phrase d'accroche, ton) |
| 5 | Vérifier le CRM (les contacts sont-ils bien créés ?) |
| 7 | Premier bilan (l'agent répond-il bien aux cas courants ?) |
| 10 | L'agent est rodé, vous êtes autonome |

**Conseil** : les premiers jours, lisez les logs régulièrement (`openclaw logs -f`) pour voir comment l'agent interagit. C'est le meilleur moyen de repérer un comportement à ajuster.

---

## En cas de panne

1. `systemctl --user status openclaw-gateway` - Le service tourne-t-il ?
2. `openclaw logs -f` - Y a-t-il une erreur visible ?
3. `openclaw whatsapp status` - Le canal est-il connecté ?
4. `openclaw gateway stop && openclaw gateway start` - Redémarrer
5. `openclaw whatsapp link` - Reliaiser le canal si déconnecté

Si rien ne fonctionne : contacter [contact d'escalade].

---

<!-- template v3.4 -->
*Généré par /agent-openclaw v3.4*
