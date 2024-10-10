from dotenv import load_dotenv
import os
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine, MetaData, Table, delete, or_, Float
from sqlalchemy.orm import sessionmaker
from elasticsearch import Elasticsearch

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Utiliser les variables d'environnement pour MySQL
host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DATABASE')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')

# Configurer Elasticsearch avec le schéma 'http'
# Ajoute le schéma 'http' dans la configuration du nœud Elasticsearch
es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))  # Conversion explicite en entier


# Ajouter le schéma 'http' dans la configuration du nœud Elasticsearch
es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])

# Vérifier la connexion à Elasticsearch
if es.ping():
    print("Connexion à Elasticsearch réussie")
else:
    print("Erreur lors de la connexion à Elasticsearch")

def create_connection():
    """Créer une connexion à MySQL"""
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
    """Obtenir la connexion à la base de données pour la requête courante"""
    if 'db' not in g:
        g.db = create_connection()
    return g.db

def close_db(e=None):
    """Fermer la connexion à la base de données à la fin de la requête"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Configurer Flask et SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{user}:{password}@{host}/{database}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser la base de données et la migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Nettoyer les connexions MySQL après chaque requête
@app.teardown_appcontext
def teardown_db(exception):
    close_db()


