# DeslinBot - Bot WhatsApp Python

## Structure du projet
```
deslinbot/
├── main.py          → Serveur webhook Flask
├── bot.py           → Logique du bot et réponses
├── conversations.py → Gestion états et rôles clients
├── requirements.txt → Dépendances Python
├── Procfile         → Configuration Railway
└── .env             → Variables secrètes (ne pas commit !)
```

## Configuration

1. Copie `.env.example` en `.env` et remplis les valeurs :
```
WHATSAPP_TOKEN=ton_token_permanent
VERIFY_TOKEN=mot_secret_que_tu_choisis (ex: deslinbot2024)
PHONE_NUMBER_ID=id_du_numero_whatsapp
```

## Trouver ton PHONE_NUMBER_ID
- Va sur developers.facebook.com
- Ton app → WhatsApp → Configuration de l'API
- Copie le "Phone number ID"

## Déploiement sur Railway

1. Crée un compte sur railway.app
2. Nouveau projet → "Deploy from GitHub"
3. Connecte ton repo GitHub
4. Dans Variables d'environnement, ajoute :
   - WHATSAPP_TOKEN
   - VERIFY_TOKEN  
   - PHONE_NUMBER_ID
5. Railway génère une URL publique (ex: deslinbot.up.railway.app)

## Configuration Webhook sur Meta

1. Va sur developers.facebook.com → ton app → WhatsApp → Configuration
2. Dans "Webhook", clique "Modifier"
3. URL de rappel : https://ton-app.up.railway.app/webhook
4. Token de vérification : la valeur de ton VERIFY_TOKEN
5. Clique "Vérifier et enregistrer"
6. Active "messages" dans les abonnements

## Commandes Admin

Envoie ces messages depuis ton numéro WhatsApp :

| Commande | Description |
|----------|-------------|
| /admin liste | Voir tous les clients |
| /admin role <tel> vip | Changer le rôle |
| /admin bloquer <tel> | Bloquer un client |
| /admin debloquer <tel> | Débloquer un client |
| /admin notif <tel> <msg> | Envoyer une notification |

## Rôles disponibles
- `client` → Client normal
- `vip` → Client VIP
- `bloque` → Client bloqué (messages ignorés)
- `admin` → Administrateur
