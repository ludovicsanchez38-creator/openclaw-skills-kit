#!/bin/bash
# Healthcheck OpenClaw - à lancer via cron toutes les 5 minutes
# Usage: bash healthcheck.sh [agent-id] [phone-propriétaire]
#
# Crontab : */5 * * * * bash /opt/clawdbot/workspace-[id]/scripts/healthcheck.sh [id] [phone]

AGENT_ID="${1:-main}"
OWNER_PHONE="${2:-}"
LOG="/tmp/openclaw-healthcheck.log"
ALERT_FILE="/tmp/openclaw-alert-sent"

# Vérifier que le gateway est en vie
if ! lsof -ti :18789 > /dev/null 2>&1; then
    echo "$(date) - Gateway DOWN - tentative de redémarrage" >> "$LOG"

    # Tenter un redémarrage
    openclaw gateway start >> "$LOG" 2>&1

    # Attendre 10 secondes et revérifier
    sleep 10

    if ! lsof -ti :18789 > /dev/null 2>&1; then
        echo "$(date) - Redémarrage ÉCHOUÉ" >> "$LOG"

        # Alerter le propriétaire (une seule fois par incident)
        if [ ! -f "$ALERT_FILE" ] && [ -n "$OWNER_PHONE" ]; then
            echo "$(date) - Alerte envoyée à $OWNER_PHONE" >> "$LOG"
            touch "$ALERT_FILE"
        fi
    else
        echo "$(date) - Gateway redémarré avec succès" >> "$LOG"
        rm -f "$ALERT_FILE"
    fi
else
    # Gateway OK - supprimer le flag d'alerte si présent
    rm -f "$ALERT_FILE"
fi

# Vérifier la mémoire QMD (toutes les 30 min seulement)
MINUTE=$(date +%M)
if [ "$((MINUTE % 30))" -eq 0 ]; then
    QMD_STATUS=$(openclaw memory status 2>&1 | grep -c "ready")
    if [ "$QMD_STATUS" -eq 0 ]; then
        echo "$(date) - QMD pas ready - reindex" >> "$LOG"
        openclaw memory index --force >> "$LOG" 2>&1
    fi
fi

# Rotation du log (garder les 1000 dernières lignes)
if [ -f "$LOG" ] && [ "$(wc -l < "$LOG")" -gt 1000 ]; then
    tail -500 "$LOG" > "${LOG}.tmp" && mv "${LOG}.tmp" "$LOG"
fi
