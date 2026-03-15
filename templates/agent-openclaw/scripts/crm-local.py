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
        phone = args.get("phone")
        db["contacts"][phone] = {
            k: v for k, v in args.items() if k != "phone"
        }
        db["contacts"][phone].update({
            "statut": "nouveau",
            "bant_budget": 0, "bant_autorite": 0, "bant_need": 0, "bant_timing": 0,
            "created_at": datetime.now().isoformat(),
            "dernier_contact": datetime.now().isoformat(),
        })
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
