from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
from flask import Flask,g

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from sqlalchemy import create_engine, MetaData, Table, delete, or_, Float

import mysql.connector

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine,Table,MetaData,delete


# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Utiliser les variables d'environnement
host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DATABASE')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')

def create_connection():
    try:
        conn = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        if conn.is_connected():
            print("Connexion à la base de données MySQL réussie")
            return conn
    except Error as e:
        print(f"Erreur lors de la connexion à MySQL : {e}")
        return None

def get_db():
    if 'db' not in g:
        g.db = create_connection()
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        
        


