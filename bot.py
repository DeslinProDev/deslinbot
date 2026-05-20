# bot.py - Logique principale du bot WhatsApp

import os
import requests
from conversations import (
    get_conversation,
    mettre_a_jour_etat,
    mettre_a_jour_nom,
    ajouter_historique,
    changer_role,
    get_role,
    est_bloque,
    lister_clients,
    terminer_conversation,
    ETATS,
    ROLES,
)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
API_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

# ─────────────────────────────────────────────
# ENVOI DE MESSAGES
# ─────────────────────────────────────────────

def envoyer_message(telephone, texte):
    """Envoie un message texte à un numéro WhatsApp."""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": telephone,
        "type": "text",
        "text": {"body": texte},
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def envoyer_notification(telephone, titre, contenu):
    """Envoie une notification formatée."""
    message = f"🔔 *{titre}*\n\n{contenu}"
    return envoyer_message(telephone, message)


def envoyer_menu_principal(telephone, nom):
    """Envoie le menu principal au client."""
    menu = (
        f"👋 Bonjour *{nom}* ! Comment puis-je vous aider aujourd'hui ?\n\n"
        "Tapez le numéro de votre choix :\n\n"
        "1️⃣ - Informations sur nos services\n"
        "2️⃣ - Passer une commande\n"
        "3️⃣ - Suivi de commande\n"
        "4️⃣ - Parler à un conseiller\n"
        "5️⃣ - Aide / FAQ\n"
        "0️⃣ - Terminer la conversation\n\n"
        "_Tapez votre choix :_"
    )
    envoyer_message(telephone, menu)


# ─────────────────────────────────────────────
# TRAITEMENT DES MESSAGES ENTRANTS
# ─────────────────────────────────────────────

def traiter_message(telephone, message_texte):
    """Point d'entrée principal pour traiter un message reçu."""

    # Vérifier si le client est bloqué
    if est_bloque(telephone):
        return  # On ignore les messages des clients bloqués

    conv = get_conversation(telephone)
    etat = conv["etat"]
    texte = message_texte.strip()

    # Enregistrer le message dans l'historique
    ajouter_historique(telephone, "client", texte)

    # Commandes admin disponibles partout
    if texte.startswith("/admin"):
        traiter_commande_admin(telephone, texte)
        return

    # Router selon l'état de la conversation
    if etat == ETATS["DEBUT"] or etat == ETATS["TERMINE"]:
        _etape_debut(telephone, texte)

    elif etat == ETATS["ATTENTE_NOM"]:
        _etape_attente_nom(telephone, texte)

    elif etat == ETATS["MENU_PRINCIPAL"]:
        _etape_menu_principal(telephone, texte)

    elif etat == ETATS["EN_CONVERSATION"]:
        _etape_en_conversation(telephone, texte)

    elif etat == ETATS["ATTENTE_COMMANDE"]:
        _etape_attente_commande(telephone, texte)


# ─────────────────────────────────────────────
# ÉTAPES DE CONVERSATION
# ─────────────────────────────────────────────

def _etape_debut(telephone, texte):
    """Accueil du client et demande du nom."""
    envoyer_message(
        telephone,
        "👋 Bienvenue ! Je suis votre assistant virtuel.\n\n"
        "Pour mieux vous servir, puis-je avoir votre *prénom* s'il vous plaît ?",
    )
    mettre_a_jour_etat(telephone, ETATS["ATTENTE_NOM"])


def _etape_attente_nom(telephone, texte):
    """Enregistre le nom et affiche le menu."""
    nom = texte.capitalize()
    mettre_a_jour_nom(telephone, nom)
    mettre_a_jour_etat(telephone, ETATS["MENU_PRINCIPAL"])
    envoyer_message(telephone, f"Merci *{nom}* ! 😊")
    envoyer_menu_principal(telephone, nom)


def _etape_menu_principal(telephone, texte):
    """Gère les choix du menu principal."""
    conv = get_conversation(telephone)
    nom = conv.get("nom", "Client")

    if texte == "1":
        envoyer_message(
            telephone,
            "ℹ️ *Nos services :*\n\n"
            "• Service A : Description du service A\n"
            "• Service B : Description du service B\n"
            "• Service C : Description du service C\n\n"
            "Tapez *menu* pour revenir au menu principal.",
        )
        mettre_a_jour_etat(telephone, ETATS["EN_CONVERSATION"])

    elif texte == "2":
        envoyer_message(
            telephone,
            "🛒 *Passer une commande*\n\n"
            "Veuillez décrire ce que vous souhaitez commander :",
        )
        mettre_a_jour_etat(telephone, ETATS["ATTENTE_COMMANDE"])

    elif texte == "3":
        envoyer_message(
            telephone,
            "📦 *Suivi de commande*\n\n"
            "Veuillez entrer votre numéro de commande :",
        )
        mettre_a_jour_etat(telephone, ETATS["EN_CONVERSATION"])

    elif texte == "4":
        envoyer_message(
            telephone,
            "👨‍💼 *Conseiller humain*\n\n"
            "Un conseiller va vous contacter dans les plus brefs délais.\n"
            "Merci de patienter. 🙏",
        )

    elif texte == "5":
        envoyer_message(
            telephone,
            "❓ *FAQ - Questions fréquentes :*\n\n"
            "• *Q: Quels sont vos horaires ?*\n  R: Lundi-Vendredi, 8h-18h\n\n"
            "• *Q: Comment passer une commande ?*\n  R: Tapez 2 dans le menu\n\n"
            "• *Q: Délai de livraison ?*\n  R: 2 à 5 jours ouvrables\n\n"
            "Tapez *menu* pour revenir.",
        )
        mettre_a_jour_etat(telephone, ETATS["EN_CONVERSATION"])

    elif texte == "0":
        envoyer_message(
            telephone,
            f"Au revoir *{nom}* ! Merci de nous avoir contactés. 👋\n"
            "N'hésitez pas à revenir si vous avez d'autres questions.",
        )
        terminer_conversation(telephone)

    else:
        envoyer_message(
            telephone,
            "❌ Choix invalide. Veuillez entrer un numéro entre 0 et 5.",
        )
        envoyer_menu_principal(telephone, nom)


def _etape_en_conversation(telephone, texte):
    """Gère la conversation libre."""
    if texte.lower() in ["menu", "retour", "accueil"]:
        conv = get_conversation(telephone)
        nom = conv.get("nom", "Client")
        mettre_a_jour_etat(telephone, ETATS["MENU_PRINCIPAL"])
        envoyer_menu_principal(telephone, nom)
    else:
        envoyer_message(
            telephone,
            "Merci pour votre message. 😊\n\n"
            "Tapez *menu* pour revenir au menu principal.",
        )


def _etape_attente_commande(telephone, texte):
    """Gère la réception d'une commande."""
    conv = get_conversation(telephone)
    nom = conv.get("nom", "Client")
    conv["commande_en_cours"] = texte

    envoyer_message(
        telephone,
        f"✅ *Commande reçue !*\n\n"
        f"📝 Détails : _{texte}_\n\n"
        f"Votre commande a bien été enregistrée *{nom}*.\n"
        f"Nous vous confirmons cela très bientôt.\n\n"
        f"Tapez *menu* pour revenir au menu.",
    )
    mettre_a_jour_etat(telephone, ETATS["EN_CONVERSATION"])


# ─────────────────────────────────────────────
# COMMANDES ADMIN
# ─────────────────────────────────────────────

def traiter_commande_admin(telephone, texte):
    """
    Commandes admin disponibles (à envoyer depuis ton numéro) :
    /admin liste          → voir tous les clients
    /admin role <tel> vip → changer le rôle d'un client
    /admin bloquer <tel>  → bloquer un client
    /admin debloquer <tel>→ débloquer un client
    /admin notif <tel> <message> → envoyer une notification
    """
    parties = texte.split(" ", 3)
    commande = parties[1] if len(parties) > 1 else ""

    if commande == "liste":
        clients = lister_clients()
        if not clients:
            envoyer_message(telephone, "Aucun client pour l'instant.")
            return
        msg = "👥 *Liste des clients :*\n\n"
        for c in clients:
            msg += (
                f"📱 {c['telephone']}\n"
                f"   Nom: {c['nom']} | Rôle: {c['role']}\n"
                f"   Messages: {c['nb_messages']}\n\n"
            )
        envoyer_message(telephone, msg)

    elif commande == "role" and len(parties) >= 4:
        tel_cible = parties[2]
        nouveau_role = parties[3]
        if changer_role(tel_cible, nouveau_role):
            envoyer_message(telephone, f"✅ Rôle de {tel_cible} changé en *{nouveau_role}*")
        else:
            envoyer_message(telephone, f"❌ Rôle invalide. Utilisez : client, vip, bloque, admin")

    elif commande == "bloquer" and len(parties) >= 3:
        tel_cible = parties[2]
        changer_role(tel_cible, ROLES["BLOQUE"])
        envoyer_message(telephone, f"🚫 Client {tel_cible} bloqué.")

    elif commande == "debloquer" and len(parties) >= 3:
        tel_cible = parties[2]
        changer_role(tel_cible, ROLES["CLIENT"])
        envoyer_message(telephone, f"✅ Client {tel_cible} débloqué.")

    elif commande == "notif" and len(parties) >= 4:
        tel_cible = parties[2]
        contenu_notif = parties[3]
        envoyer_notification(tel_cible, "Notification", contenu_notif)
        envoyer_message(telephone, f"✅ Notification envoyée à {tel_cible}")

    else:
        envoyer_message(
            telephone,
            "📋 *Commandes admin disponibles :*\n\n"
            "/admin liste\n"
            "/admin role <tel> <role>\n"
            "/admin bloquer <tel>\n"
            "/admin debloquer <tel>\n"
            "/admin notif <tel> <message>",
        )
