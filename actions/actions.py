import json
import uuid
import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class action_make_reservation(Action):
    def name(self) -> Text:
        return "action_create_reservation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Obtenir les détails de la réservation depuis les entités extraites par Rasa
        reservation_name = tracker.get_slot("reservation_name")
        date = tracker.get_slot("date")
        number_of_people = tracker.get_slot("number_of_people")
        phone_number = tracker.get_slot("phone_number")
        comment = tracker.get_slot("comment")  # Nouveau champ de commentaire

        # Générer un UUID pour le numéro de réservation
        reservation_number = str(uuid.uuid4())

        # Créer un dictionnaire pour la nouvelle réservation
        new_reservation = {
            "reservation_number": reservation_number,
            "reservation_name": reservation_name,
            "date": date,
            "number_of_people": number_of_people,
            "phone_number": phone_number,
            "comment": comment  # Ajout du champ de commentaire
        }

        # Charger les réservations existantes depuis le fichier JSON
        file_path = os.path.join(os.path.dirname(__file__), "reservation.json")
        with open(file_path, "r") as file:
            reservations = json.load(file)

        # Ajouter la nouvelle réservation à la liste des réservations
        reservations.append(new_reservation)

        # Enregistrer les réservations mises à jour dans le fichier JSON
        with open(file_path, "w") as file:
            json.dump(reservations, file, indent=4)

        dispatcher.utter_message("La réservation a été créée avec succès.")
        return []


class action_cancel_reservation(Action):
    def name(self) -> Text:
        return "action_delete_reservation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Obtenir le numéro de réservation depuis les entités extraites par Rasa
        reservation_number = tracker.get_slot("reservation_number")
        reservation_name = tracker.get_slot("reservation_name")

        # Charger les réservations depuis le fichier JSON
        file_path = os.path.join(os.path.dirname(__file__), "reservation.json")
        with open(file_path, "r") as file:
            reservations = json.load(file)

        # Rechercher la réservation à supprimer par le numéro ou le nom
        for reservation in reservations:
            if reservation["reservation_number"] == reservation_number or reservation["reservation_name"] == reservation_name:
                # Supprimer la réservation de la liste
                reservations.remove(reservation)

        # Enregistrer les réservations mises à jour dans le fichier JSON
        with open(file_path, "w") as file:
            json.dump(reservations, file, indent=4)

        dispatcher.utter_message("La réservation a été supprimée avec succès.")
        return []


class ActionCheckAvailability(Action):
    def name(self) -> Text:
        return "action_check_availability"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Obtenir la date spécifiée par l'utilisateur
        date = tracker.get_slot("date")
        max_capacity = 20  # constante aléatoire du nombre de tables

        # Charger les réservations depuis le fichier JSON
        file_path = os.path.join(os.path.dirname(__file__), "reservation.json")
        with open(file_path, "r") as file:
            reservations = json.load(file)

        # Compter le nombre de réservations pour la date spécifiée
        reservations_for_date = [reservation for reservation in reservations if reservation["date"] == date]
        number_of_reservations_for_date = len(reservations_for_date)

        # Vérifier si le nombre de réservations dépasse 20
        if number_of_reservations_for_date >= max_capacity:
            dispatcher.utter_message("Désolé, toutes les tables sont réservées pour la date spécifiée.")
        else:
            dispatcher.utter_message("Les tables sont disponibles pour la date spécifiée.")

        return []


class ActionDisplayReservationInformation(Action):
    def name(self) -> Text:
        return "action_display_reservation_information"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Obtenir le numéro de réservation depuis les entités extraites par Rasa
        reservation_number = tracker.get_slot("reservation_number")

        # Charger les réservations depuis le fichier JSON
        file_path = os.path.join(os.path.dirname(__file__), "reservation.json")
        with open(file_path, "r") as file:
            reservations = json.load(file)

        # Rechercher la réservation correspondant au numéro spécifié
        for reservation in reservations:
            if reservation["reservation_number"] == reservation_number:
                # Envoyer les détails de la réservation à l'utilisateur
                message = f"Voici les détails de votre réservation:\nNom: {reservation['reservation_name']}\nDate: {reservation['date']}\nNombre de personnes: {reservation['number_of_people']}\nNuméro de téléphone: {reservation['phone_number']}\nCommentaire: {reservation['comment']}"  # Ajout du champ de commentaire
                dispatcher.utter_message(message)
                break
        else:
            dispatcher.utter_message("Désolé, je n'ai pas trouvé de réservation avec ce numéro.")

        return []


class ActionModifyComment(Action):
    def name(self) -> Text:
        return "action_modify_comment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Obtenir le numéro de réservation et le nouveau commentaire depuis les entités extraites par Rasa
        reservation_number = tracker.get_slot("reservation_number")
        new_comment = tracker.get_slot("new_comment")
        
        # Charger les réservations depuis le fichier JSON
        file_path = os.path.join(os.path.dirname(__file__), "reservation.json")
        with open(file_path, "r") as file:
            reservations = json.load(file)

        # Rechercher la réservation correspondant au numéro spécifié
        for reservation in reservations:
            if reservation["reservation_number"] == reservation_number:
                # Mettre à jour le commentaire de la réservation
                reservation["comment"] = new_comment
                break
        
        # Enregistrer les réservations mises à jour dans le fichier JSON
        with open(file_path, "w") as file:
            json.dump(reservations, file, indent=4)

        dispatcher.utter_message("Le commentaire de la réservation a été modifié avec succès.")
        return []

class action_get_reservation_number(Action):
    def name(self) -> Text:
        return "action_get_reservation_number"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Charger les réservations depuis le fichier JSON
        file_path = os.path.join(os.path.dirname(__file__), "reservation.json")
        with open(file_path, "r") as file:
            reservations = json.load(file)

        # Obtenir les informations de la dernière réservation
        last_reservation = reservations[-1] if reservations else None

        if last_reservation:
            reservation_number = last_reservation.get("reservation_number")
            if reservation_number:
                dispatcher.utter_message(f"Le numéro de votre réservation est : {reservation_number}")
            else:
                dispatcher.utter_message("Désolé, nous n'avons pas pu récupérer le numéro de votre réservation.")
        else:
            dispatcher.utter_message("Désolé, aucune réservation n'a été trouvée.")

        return []