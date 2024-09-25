from flask import Flask, render_template, request, redirect, url_for, flash, session,send_file
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

from flask_migrate import Migrate
import os
import logging
import my_queries as qr
import data as dt
import config as cf
import pandas as pd




app = Flask(__name__)

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)

# Configuration de la clé secrète pour les sessions Flask
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'votre_clé_secrète')

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisation de la base de données et de la migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# On a une liste sur les régions de la CI, en effet elle est la page principale
@app.route('/')
def list_regions():
    regions = qr.options_regions()
    map_html = dt.statistiques()
    coord_list = []  # Remplacez par vos données de coordonnées si nécessaire
    return render_template('home.html', regions=regions,coord_list=coord_list, map_html= map_html)







#Pour les requetes:
# Fonction pour charger les données CSV
def get_data(filepath):
    df = pd.read_csv(filepath, sep=',')
    return df


def get_data_from_mysql():
    # Configurer les informations de connexion à la base de données MySQL
    conn = cf.create_connection()
    # Requête SQL pour sélectionner toutes les données
    query = "SELECT * FROM valeur_indicateur_libelle"

    # Charger les données dans un DataFrame pandas
    df = pd.read_sql(query, conn)

    # Fermer la connexion
    conn.close()

    return df

# Route pour récupérer les départements en fonction de la région sélectionnée
@app.route('/get_departements', methods=['GET'])
def get_departements():
    region = request.args.get('region')
    df = get_data_from_mysql()  # Récupère les données
    departements = df[df['nom_region'] == region]['nom_departement'].sort_values().unique()
    return jsonify(list(departements))


# Route pour récupérer les sous-préfectures en fonction du département sélectionné
@app.route('/get_sous_prefectures', methods=['GET'])
def get_sous_prefectures():
    departement = request.args.get('departement')
    df = get_data_from_mysql()  # Récupère les données
    sous_prefectures = df[df['nom_departement'] == departement]['nom_sousprefecture'].sort_values().unique()
    return jsonify(list(sous_prefectures))


# Route pour afficher la page de requête
@app.route('/request_indicateur', methods=['GET', 'POST'])
def request_indicateur():
    # Charger les données depuis MySQL
    df = get_data_from_mysql()

    # Obtenir les options pour chaque filtre (indicateur, région, etc.)
    indicateurs_options = qr.options_indicateur()
    regions = df['nom_region'].dropna().sort_values().unique()
    departements = df['nom_departement'].dropna().sort_values().unique()
    sous_prefectures = df['nom_sousprefecture'].dropna().sort_values().unique()

    if request.method == 'POST':
        # Récupérer les sélections de l'utilisateur
        indicateur_SELECT = request.form.get('indicateur')
        region_SELECT = request.form.get('region')
        departement_SELECT = request.form.get('departement')
        sousprefecture_SELECT = request.form.get('sous_prefecture')

        # Commencer avec l'ensemble complet des données, sans certaines colonnes inutiles
        df_filtered = df.drop(columns=['statut', 'id'], errors='ignore')

        # Filtrer par indicateur sélectionné
        if indicateur_SELECT:
            df_filtered = df_filtered[df_filtered['nom_indicateur'] == indicateur_SELECT]

        # Premier résultat après filtre indicateur
        print("Premier résultat :", df_filtered.head())

        # Appliquer les filtres supplémentaires en fonction des sélections
        if sousprefecture_SELECT:
            df_filtered = df_filtered[df_filtered['nom_sousprefecture'] == sousprefecture_SELECT]
            # Supprimer les colonnes région et département si sous-préfecture est sélectionnée
            df_filtered = df_filtered.drop(columns=['nom_region', 'nom_departement'], errors='ignore')

        elif departement_SELECT:
            df_filtered = df_filtered[
                (df_filtered['nom_departement'] == departement_SELECT) &
                (df_filtered['nom_region'] == region_SELECT)
            ]
            # Supprimer la colonne région si département est sélectionné
            df_filtered = df_filtered.drop(columns=['nom_region'], errors='ignore')

        elif region_SELECT:
            df_filtered = df_filtered[df_filtered['nom_region'] == region_SELECT]

        # Deuxième résultat après application de tous les filtres
        print("Résultat 2 :", df_filtered.head())

        # Supprimer les colonnes contenant uniquement des NaN
        df_filtered = df_filtered.dropna(axis=1, how='all')

        # Vérifier si le DataFrame filtré est vide
        if df_filtered.empty:
            message = "Aucune donnée disponible pour les critères sélectionnés."
            return render_template('result.html', available_columns=[], message=message)
        else:
            # Stocker le DataFrame filtré dans la session (au format JSON)
            session['df_filtered'] = df_filtered.to_json()

            # Obtenir les colonnes disponibles pour la zone de dépôt
            available_columns = list(df_filtered.columns)

            # Afficher la page résultat avec les colonnes disponibles
            return render_template('result.html', available_columns=available_columns, message="", indicateur_SELECT=indicateur_SELECT)

    # Si GET, afficher la page de sélection avec les options de filtre
    return render_template(
        'requete_indicateur.html',
        indicateurs=indicateurs_options,
        regions=regions,
        departements=departements,
        sous_prefectures=sous_prefectures
    )



# Route pour générer le tableau croisé
@app.route('/generate_pivot_table', methods=['POST'])
def generate_pivot_table():
    data = request.get_json()
    selected_columns = data.get('columns', [])

    # Recharger le DataFrame filtré depuis la session
    df_filtered_json = session.get('df_filtered', None)
    print("Vérification du DataFrame JSON:", df_filtered_json)

    if df_filtered_json:
        # Convertir le JSON en DataFrame
        df = pd.read_json(df_filtered_json)
        
        if selected_columns:
            # Filtrer le DataFrame pour ne conserver que les colonnes sélectionnées
            df_filtered = df[selected_columns]

            # Convertir en HTML pour l'affichage dans la table
            table_html = df_filtered.to_html(classes='table table-bordered', index=False)

            return jsonify({"table_html": table_html})

    # Si aucune colonne sélectionnée ou DataFrame vide, renvoyer un message par défaut
    return jsonify({"table_html": "<p>Aucune colonne sélectionnée</p>"})


import io

# Pour télécharger le tableau en Excel
@app.route('/download_excel')
def download_excel():
    selected_columns = request.args.get('columns', '').split(',')

    # Vérifier si des colonnes ont été sélectionnées
    if not selected_columns or selected_columns == ['']:
        return "<p>Aucune variable n'a été sélectionnée pour le téléchargement</p>"

    # Reload filtered dataframe from session
    df_filtered_json = session.get('df_filtered', None)

    if df_filtered_json:
        df = pd.read_json(df_filtered_json)

        # Générer le tableau croisé dynamique en utilisant les colonnes sélectionnées
        pivot_table = pd.pivot_table(df, values='Valeur', index=selected_columns)

        # Créer un fichier Excel en mémoire
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pivot_table.to_excel(writer, index=True)

        # Déplacer le curseur au début du fichier
        output.seek(0)

        # Retourner le fichier Excel à télécharger
        return send_file(output, download_name='tableau_pivot.xlsx', as_attachment=True)
    else:
        return "<p>Aucune donnée disponible pour téléchargement</p>"



# Debut du  dash bord région avec leur carte

@app.route('/dash_region', methods=['GET', 'POST'])
def dash_region():
    return render_template('dash_region.html')


#Fin du das bord avec les régions de la CI

if __name__ == '__main__':
    app.run(debug=True)
