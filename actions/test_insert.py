import sqlite3

def test_insert():
    db_name = "restaurant.db"
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS reservation(code TEXT PRIMARY KEY, date TEXT, num_people TEXT, telephone TEXT, comment TEXT, name TEXT)")
            cursor.execute("INSERT INTO reservation (code, date, num_people, telephone, comment, name) VALUES (?, ?, ?, ?, ?, ?)",
                           ("12345678", "13/10/2000", "6", "06123454", "Pas de commentaire", "M.Auger"))
            conn.commit()
            print("Insertion réussie.")
    except sqlite3.IntegrityError as e:
        print(f"Erreur d'intégrité SQLite: {e}")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_insert()


def test_retrieve():
    db_name = "restaurant.db"
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reservation")
            reservations = cursor.fetchall()
            print("Réservations:")
            for reservation in reservations:
                print(reservation)
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    test_retrieve()
