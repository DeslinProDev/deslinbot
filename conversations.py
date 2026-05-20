# conversations.py - Gestion des conversations et rôles clients

# États possibles d'une conversation
ETATS = {
    "DEBUT": "debut",
    "ATTENTE_NOM": "attente_nom",
    "MENU_PRINCIPAL": "menu_principal",
    "ATTENTE_QUESTION": "attente_question",
    "EN_CONVERSATION": "en_conversation",
    "ATTENTE_COMMANDE": "attente_commande",
    "TERMINE": "termine",
}

# Rôles possibles pour un client
ROLES = {
    "CLIENT": "client",
    "VIP": "vip",
    "BLOQUE": "bloque",
    "ADMIN": "admin",
}

# Stockage en mémoire des conversations actives
# Format: { "numero_telephone": { "etat": ..., "nom": ..., "role": ..., "historique": [...] } }
conversations = {}


def get_conversation(telephone):
    """Récupère ou crée une conversation pour un numéro."""
    if telephone not in conversations:
        conversations[telephone] = {
            "etat": ETATS["DEBUT"],
            "nom": None,
            "role": ROLES["CLIENT"],
            "historique": [],
            "commande_en_cours": None,
        }
    return conversations[telephone]


def mettre_a_jour_etat(telephone, nouvel_etat):
    """Met à jour l'état d'une conversation."""
    conv = get_conversation(telephone)
    conv["etat"] = nouvel_etat


def mettre_a_jour_nom(telephone, nom):
    """Enregistre le nom du client."""
    conv = get_conversation(telephone)
    conv["nom"] = nom


def ajouter_historique(telephone, role_msg, contenu):
    """Ajoute un message à l'historique de la conversation."""
    conv = get_conversation(telephone)
    conv["historique"].append({"role": role_msg, "contenu": contenu})
    # Garder seulement les 20 derniers messages
    if len(conv["historique"]) > 20:
        conv["historique"] = conv["historique"][-20:]


def changer_role(telephone, nouveau_role):
    """Change le rôle d'un client."""
    if nouveau_role not in ROLES.values():
        return False
    conv = get_conversation(telephone)
    conv["role"] = nouveau_role
    return True


def get_role(telephone):
    """Retourne le rôle d'un client."""
    conv = get_conversation(telephone)
    return conv.get("role", ROLES["CLIENT"])


def est_bloque(telephone):
    """Vérifie si un client est bloqué."""
    return get_role(telephone) == ROLES["BLOQUE"]


def lister_clients():
    """Retourne la liste de tous les clients avec leurs infos."""
    return [
        {
            "telephone": tel,
            "nom": info.get("nom", "Inconnu"),
            "role": info.get("role", ROLES["CLIENT"]),
            "etat": info.get("etat"),
            "nb_messages": len(info.get("historique", [])),
        }
        for tel, info in conversations.items()
    ]


def terminer_conversation(telephone):
    """Termine et réinitialise une conversation."""
    if telephone in conversations:
        conversations[telephone]["etat"] = ETATS["TERMINE"]
        conversations[telephone]["commande_en_cours"] = None
