import sqlite3

# Establish connection
conn = sqlite3.connect('restaurant.db')

# Create cursor
cursor = conn.cursor()