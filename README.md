# Chatbot-Rasa 🤖
Ce projet, réalisé en partenariat avec l'école Epsi, vise à approfondir l'apprentissage des technologies de pointe en concevant un **chatbot** dédié à la réservation de restaurants. En utilisant la puissante plateforme **Rasa**, nous explorons les capacités de **l'intelligence artificielle conversationnelle**, permettant ainsi une interaction fluide et efficace avec les utilisateurs.

# Preview 🖼️

![image](https://github.com/BenoitAd/Chatbot-Rasa/assets/62358946/a957c63c-b5c9-465c-92f6-9e3cbc679f3a)


# Instructions & Intégration 🗒️

**Étape 0 :** Assurez-vous d'avoir configuré **Rasa** sur votre système ou serveur.

**Étape 1 :** Comme cette interface de chat communique avec le serveur Rasa via le canal REST, assurez-vous que le canal soit ajouté dans le fichier **credentials.yml**. (facultatif)

**Étape 2 :** Démarrer le server **Rasa** a l'aide de cette commande : 

```shell
rasa run -m models --enable-api --cors "*" --debug
```

**Étape 3 :** Nous avons des actions personnalisées, vous devez donc **démarrer le serveur d'actions** en utilisant la **commande** suivante :

```shell
rasa run actions --cors "*" --debug
```

**Notes :** Si vous exécutez le serveur Rasa sur un **serveur distant** comme une instance EC2, il est nécessaire de modifier le fichier **constants.js** et de remplacer **"localhost"** par **l'adresse IP publique du serveur**.

**Étape 4 :** Une fois que votre serveur Rasa est opérationnel, vous pouvez tester le bot en exécutant le fichier **index.html** dans le navigateur.
