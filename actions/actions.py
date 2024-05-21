# Database Part
import sqlite3

import datetime
# This is a simple example for a custom action which utters "Hello World!"
import random
from typing import Any, Text, Dict, List
from datetime import datetime
import time
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect('restaurant.db')
        self.cursor = self.conn.cursor()

    def test_connection(self):
        if self.conn is None:
            try:
                # Tentative de connexion à la base de données
                self.conn = sqlite3.connect(self.db_name)
                print("Connexion à la base de données réussie.")
            except sqlite3.Error as e:
                # En cas d'erreur lors de la connexion
                print(f"Erreur de connexion à la base de données : {e}")
                raise  # Relever l'erreur pour la gérer dans la méthode run()

    def create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.cursor().execute("CREATE TABLE IF NOT EXISTS reservation(code TEXT PRIMARY KEY, date TEXT, num_people TEXT, telephone TEXT, comment TEXT, name TEXT)")

    def retrieve_entry(self, code):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reservation WHERE code=?", (code,))
            result = cursor.fetchone()
            return result if result is not None else None

    def delete_entry(self, code):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reservation WHERE code=?", (code,))
            # Return None if no row was affected (i.e., no entry with that code exists)
            return cursor.fetchone() if cursor.rowcount > 0 else None

    def insert_entry(self, code, date, num_people, telephone, comment=None, name=None):
        with sqlite3.connect(self.db_name) as conn:
            conn.cursor().execute("INSERT INTO reservation (code, date, num_people, telephone, comment, name) VALUES (?, ?, ?, ?, ?, ?)",
                                  (code, date, num_people, telephone, comment, name))
            conn.commit()

# Initialiser le compteur
counter = 0

def generate_unique_id():
    global counter
    # Obtenir l'horodatage actuel (en millisecondes)
    timestamp = str(int(time.time() * 1000))
    # Incrémenter le compteur
    counter += 1
    # Concaténer l'horodatage et le compteur pour former l'identifiant
    unique_id = timestamp + str(counter)
    return unique_id

class Reservation:
    def __init__(self, code, date, num_people, telephone, comment=None, name=None):
        self.date = date
        self.code = code
        self.num_people = num_people
        self.telephone = telephone
        self.comment = comment
        self.name = name

    def __str__(self):
        return f"Reservation details: Date={self.date}, Time={self.code}, Num num_people={self.num_people},Telephone={self.telephone}, Comment={self.comment}, Name={self.name}"

class ActionManageDate(Action):

    def name(self) -> Text:
        return "action_add_date"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db = Database("restaurant.db")
        db.create_table()

        date = tracker.get_slot("date")
        response = f"Vous avez reservé pour le : {date}"

        dispatcher.utter_message(text=response)

        return [SlotSet("date", date)]


class ActionManagePeople(Action):

    def name(self) -> Text:
        return "action_add_people"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        number_of_people = tracker.get_slot("num_people")

        response = f"Vous avez reservé pour : {number_of_people} personne(s)"
        dispatcher.utter_message(text=response)

        return [SlotSet("num_people", number_of_people)]
    
class ActionManageTelephone(Action):
    
        def name(self) -> Text:
            return "action_add_telephone"
    
        def run(self, dispatcher: CollectingDispatcher,
                tracker: Tracker,
                domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            telephone = tracker.get_slot("telephone")
    
            response = f"Votre numéro de téléphone : {telephone}"
            dispatcher.utter_message(text=response)
    
            return [SlotSet("telephone", telephone)]
        
class ActionManageComment(Action):
        
            def name(self) -> Text:
                return "action_add_comment"
        
            def run(self, dispatcher: CollectingDispatcher,
                    tracker: Tracker,
                    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
                comment = tracker.get_slot("comment")
        
                response = f"Votre commentaire : {comment}"
                # Ask for the reservation comment
                dispatcher.utter_message(text=response)
        
                return [SlotSet("comment", comment)]
            
class ActionManageName(Action):
    
    def name(self) -> Text:
        return "action_add_name"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("name")
    
        response = f"Votre nom : {name}"
        # Ask for the reservation name
        dispatcher.utter_message(text=response)
    
        return [SlotSet("name", name)]

class ActionConfirmation(Action):

    def name(self) -> Text:
        return "action_confirm_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


            # Récupérer les données à insérer
            date = str(tracker.get_slot("date"))
            num_people = str(tracker.get_slot("num_people"))
            code = generate_unique_id()
            telephone = str(tracker.get_slot("telephone"))
            comment = str(tracker.get_slot("comment") or "Pas de commentaire")
            name = str(tracker.get_slot("name"))

            # Réponse à l'utilisateur
            response = (
                f"Vous avez réservé pour {num_people} personnes pour le {date}.\n"
                f"Votre numéro de réservation est le {code}.\n"
                f"Votre numéro de téléphone est le {telephone}.\n"
                f"Votre commentaire est : {comment}.\n"
                f"Votre nom est : {name}.\n"
                f"Merci pour votre réservation ! Vous avez 15 secondes pour noter votre numéro de réservation pour toute modification ou annulation."
            )
            dispatcher.utter_message(text=response)

            return []

class ActionMakeReservation(Action):
    
    def name(self) -> Text:
        return "action_make_reservation"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            with sqlite3.connect("restaurant.db") as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS reservation(code TEXT PRIMARY KEY, date TEXT, num_people TEXT, telephone TEXT, comment TEXT, name TEXT)")
                # Récupérer les données à insérer
                date = str(tracker.get_slot("date"))
                num_people = str(tracker.get_slot("num_people"))
                code = generate_unique_id()
                telephone = str(tracker.get_slot("telephone"))
                comment = str(tracker.get_slot("comment") or "Pas de commentaire")
                name = str(tracker.get_slot("name"))
                cursor.execute("INSERT INTO reservation (code, date, num_people, telephone, comment, name) VALUES (?, ?, ?, ?, ?, ?)",
                            (code, date, num_people, telephone, comment, name))
                conn.commit()
                print("Insertion réussie.")
        except sqlite3.IntegrityError as e:
            print(f"Erreur d'intégrité SQLite: {e}")
        except Exception as e:
            print(f"Erreur: {e}")
        
        return []



class AskRetrieveReservation(Action):

    def name(self) -> Text:
        return "action_retrieve_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = str(tracker.get_slot("name"))
        db = Database("restaurant.db")
        result = db.retrieve_entry(name)
        if(result):
            reservation = Reservation(result[0], result[1], result[2], result[3], result[4], result[5])
            print(reservation)
            dispatcher.utter_message(text="Voici les les détails de votre réservation :")
            dispatcher.utter_message(text=reservation.__str__())
        else:
            dispatcher.utter_message("Le nom n'est pas valide")

        return []

class ActionDeleteReservation(Action):

    def name(self) -> Text:
        return "action_delete_reservation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        code = str(tracker.get_slot("code"))

        db = Database("restaurant.db")
        result = db.retrieve_entry(code)
        if(result):
            reservation = Reservation(result[0], result[1], result[2])
            print(reservation)
            response = f"Voici votre code : {code}"
            dispatcher.utter_message(text=response)
            dispatcher.utter_message(text="Voici les les détails de votre réservation :")
            dispatcher.utter_message(text=reservation.__str__())
            db.delete_entry(code)
            dispatcher.utter_message(text="Votre réservation est bien supprimé")

        else:
            dispatcher.utter_message("Le code n'est pas valide")

        return []
