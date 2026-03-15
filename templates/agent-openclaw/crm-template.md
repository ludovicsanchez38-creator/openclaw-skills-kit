# CRM Minimal - Structure Google Sheets

## Option A : Google Sheets (recommandé pour démarrer)

### Structure de la feuille "Contacts"

| Colonne | Type | Description |
|---------|------|-------------|
| A: phone | Texte | Numéro au format +33... (clé unique) |
| B: prenom | Texte | Prénom du contact |
| C: nom | Texte | Nom de famille |
| D: entreprise | Texte | Nom de l'entreprise |
| E: secteur | Texte | Secteur d'activité |
| F: source | Texte | whatsapp, email, site, recommandation |
| G: statut | Texte | nouveau, qualifie, rdv_pris, client, inactif |
| H: bant_budget | Nombre | 0-3 |
| I: bant_autorite | Nombre | 0-3 |
| J: bant_need | Nombre | 0-3 |
| K: bant_timing | Nombre | 0-3 |
| L: bant_total | Formule | =H+I+J+K |
| M: offre_discutee | Texte | Nom de l'offre |
| N: rdv_date | Date | Date du RDV si pris |
| O: dernier_contact | Date | Date du dernier échange |
| P: prochaine_relance | Date | Date de la prochaine relance |
| Q: notes | Texte | Notes libres (dernier résumé) |
| R: langue | Texte | FR, EN |
| S: created_at | Date | Date de création |

### Structure de la feuille "SAV" (si mode SAV/Polyvalent)

| Colonne | Type | Description |
|---------|------|-------------|
| A: ticket_id | Texte | SAV-001, SAV-002... (auto-incrémenté) |
| B: phone | Texte | Numéro du client |
| C: prenom | Texte | Prénom |
| D: description | Texte | Description du problème |
| E: categorie | Texte | technique, facturation, contenu, suivi, autre |
| F: priorite | Texte | basse, moyenne, haute |
| G: statut | Texte | ouvert, en_cours, resolu, escalade |
| H: offre | Texte | Offre concernée |
| I: resolution | Texte | Comment le problème a été résolu |
| J: escalade | Texte | oui/non |
| K: created_at | Date | Date d'ouverture |
| L: updated_at | Date | Dernière mise à jour |

### Apps Script pour API CRM

Déployer ce script comme Web App (Exécuter en tant que : moi, Accès : toute personne) :

```javascript
function doPost(e) {
  var data = JSON.parse(e.postData.contents);
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Contacts");

  switch(data.command) {
    case "lookup":
      return lookup(sheet, data.args.phone);
    case "create":
      return create(sheet, data.args);
    case "update":
      return update(sheet, data.args.phone, data.args.data);
    case "list_relances":
      return listRelances(sheet);
    default:
      return ContentService.createTextOutput(JSON.stringify({error: "Commande inconnue"}));
  }
}

function lookup(sheet, phone) {
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] === phone) {
      var result = {};
      headers.forEach(function(h, j) { result[h] = data[i][j]; });
      return ContentService.createTextOutput(JSON.stringify(result));
    }
  }
  return ContentService.createTextOutput(JSON.stringify(null));
}

function create(sheet, args) {
  sheet.appendRow([
    args.phone, args.prenom || "", args.nom || "", args.entreprise || "",
    args.secteur || "", args.source || "whatsapp", "nouveau",
    0, 0, 0, 0, "=H" + (sheet.getLastRow()+1) + "+I" + (sheet.getLastRow()+1) + "+J" + (sheet.getLastRow()+1) + "+K" + (sheet.getLastRow()+1),
    "", "", new Date(), "", "", args.langue || "FR", new Date()
  ]);
  return ContentService.createTextOutput(JSON.stringify({status: "created"}));
}

function update(sheet, phone, updates) {
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  for (var i = 1; i < data.length; i++) {
    if (data[i][0] === phone) {
      Object.keys(updates).forEach(function(key) {
        var col = headers.indexOf(key);
        if (col >= 0) sheet.getRange(i+1, col+1).setValue(updates[key]);
      });
      return ContentService.createTextOutput(JSON.stringify({status: "updated"}));
    }
  }
  return ContentService.createTextOutput(JSON.stringify({error: "Contact non trouvé"}));
}

function listRelances(sheet) {
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  var today = new Date();
  today.setHours(0,0,0,0);
  var results = [];
  for (var i = 1; i < data.length; i++) {
    var relanceDate = data[i][headers.indexOf("prochaine_relance")];
    if (relanceDate && new Date(relanceDate) <= today) {
      var result = {};
      headers.forEach(function(h, j) { result[h] = data[i][j]; });
      results.push(result);
    }
  }
  return ContentService.createTextOutput(JSON.stringify(results));
}
```

### Utilisation depuis l'agent

```bash
# Lookup
curl -s -X POST "[WEBAPP_URL]" -H "Content-Type: application/json" \
  -d '{"command":"lookup","args":{"phone":"+33612345678"}}'

# Create
curl -s -X POST "[WEBAPP_URL]" -H "Content-Type: application/json" \
  -d '{"command":"create","args":{"phone":"+33612345678","prenom":"Marie","source":"whatsapp"}}'

# Update
curl -s -X POST "[WEBAPP_URL]" -H "Content-Type: application/json" \
  -d '{"command":"update","args":{"phone":"+33612345678","data":{"bant_budget":2,"notes":"Intéressée par offre X"}}}'
```

## Option B : JSON local (ultra-simple, pas de setup)

Fichier `data/crm.json` dans le workspace :

```json
{
  "contacts": {},
  "sav": []
}
```

Script Python `scripts/crm-local.py` pour manipuler :

```python
#!/usr/bin/env python3
"""CRM local en JSON. Usage: python3 crm-local.py '{"command":"lookup","args":{"phone":"+33..."}}'"""
import json, sys, os
from datetime import datetime
from pathlib import Path

CRM_PATH = Path(__file__).parent.parent / "data" / "crm.json"

def load():
    if CRM_PATH.exists():
        return json.loads(CRM_PATH.read_text())
    return {"contacts": {}, "sav": []}

def save(data):
    CRM_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))

def main():
    req = json.loads(sys.argv[1])
    cmd = req["command"]
    args = req.get("args", {})
    db = load()

    if cmd == "lookup":
        result = db["contacts"].get(args["phone"])
        print(json.dumps(result, ensure_ascii=False, default=str))

    elif cmd == "create":
        phone = args.pop("phone")
        db["contacts"][phone] = {
            **args,
            "statut": "nouveau",
            "bant_budget": 0, "bant_autorite": 0, "bant_need": 0, "bant_timing": 0,
            "created_at": datetime.now().isoformat(),
            "dernier_contact": datetime.now().isoformat(),
        }
        save(db)
        print(json.dumps({"status": "created"}))

    elif cmd == "update":
        phone = args["phone"]
        if phone in db["contacts"]:
            db["contacts"][phone].update(args.get("data", {}))
            db["contacts"][phone]["dernier_contact"] = datetime.now().isoformat()
            save(db)
            print(json.dumps({"status": "updated"}))
        else:
            print(json.dumps({"error": "Contact non trouvé"}))

    elif cmd == "list_relances":
        today = datetime.now().date().isoformat()
        relances = [
            {**v, "phone": k}
            for k, v in db["contacts"].items()
            if v.get("prochaine_relance", "") <= today and v.get("statut") != "client"
        ]
        print(json.dumps(relances, ensure_ascii=False, default=str))

    elif cmd == "sav_create":
        ticket_id = f"SAV-{len(db['sav'])+1:03d}"
        db["sav"].append({
            "ticket_id": ticket_id,
            "phone": args["phone"],
            "description": args.get("description", ""),
            "categorie": args.get("categorie", "autre"),
            "priorite": args.get("priorite", "moyenne"),
            "statut": "ouvert",
            "created_at": datetime.now().isoformat(),
        })
        save(db)
        print(json.dumps({"status": "created", "ticket_id": ticket_id}))

    elif cmd == "sav_list":
        tickets = [t for t in db["sav"] if t["phone"] == args["phone"]]
        if "statut" in args:
            tickets = [t for t in tickets if t["statut"] == args["statut"]]
        print(json.dumps(tickets, ensure_ascii=False, default=str))

    else:
        print(json.dumps({"error": f"Commande inconnue: {cmd}"}))

if __name__ == "__main__":
    main()
```

L'option B est idéale pour démarrer immédiatement. Migrer vers Google Sheets plus tard si besoin.
