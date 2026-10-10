
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )

        print("Connected to MySQL successfully!")

        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM `sample - superstore`"
        )

        row_count = cursor.fetchone()[0]
        print(f"Superstore dataset rows: {row_count}")

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        print(f"MySQL connection error: {error}")

if __name__ == "__main__":
    connect_to_database()
