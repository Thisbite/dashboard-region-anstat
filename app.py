from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
import my_queries as qr
import data as dt
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

# Route pour afficher la page de requête
@app.route('/request_indicateur', methods=['GET', 'POST'])
def request_indicateur():
    # Chargement des données
    xpath = "region_poro1.csv"
    df = get_data(xpath)
    indicateurs = df["nom_indicateur"].sort_values().unique()  # Obtenir les indicateurs
    dict_niveau = {}

    # Gestion du formulaire
    if request.method == 'POST':
        indicateur_SELECT = request.form.get('indicateur')
        region_SELECT = request.form.get('region')
        departement_SELECT = request.form.get('departement')
        sp_SELECT = request.form.get('sous_prefecture')
        Bouton_recherche = request.form.get('recherche')

        if indicateur_SELECT:
            # Filtrer les données par indicateur sélectionné
            df = df[df['nom_indicateur'] == indicateur_SELECT]
            df = df.dropna(axis=1, how='all')  # Supprime les colonnes vides

            # Obtenir les colonnes de niveau de désagrégation
            liste_col = list(df.columns)
            if 'Annee' in liste_col:
                start = liste_col.index('Annee')
                liste_niveau_desagregation = liste_col[start:-1]
            else:
                flash("La colonne 'Annee' est manquante dans les données.", "error")

            # Filtrage par région
            if region_SELECT:
                df = df[df['nom_region'] == region_SELECT]

                # Filtrage par département
                if departement_SELECT:
                    df = df[df['nom_departement'] == departement_SELECT]

                    # Filtrage par sous-préfecture
                    if sp_SELECT:
                        df = df[df['nom_sousprefecture'] == sp_SELECT]

            # Application des filtres dynamiques selon les niveaux de désagrégation
            for i, niveau in enumerate(liste_niveau_desagregation):
                dict_niveau[f"niveau{i}"] = request.form.get(f"niveau{i}")
                if dict_niveau[f"niveau{i}"]:
                    df = df[df[niveau] == dict_niveau[f"niveau{i}"]]

            if Bouton_recherche:
                # Vérifier si le DataFrame filtré n'est pas vide
                if df.empty:
                    flash("Désolé, aucune donnée disponible pour la sélection actuelle.", "error")
                else:
                    return render_template('result.html', df=df)  # Affiche les résultats dans un template HTML

    # Variables à envoyer au template pour affichage
    regions = df["nom_region"].sort_values().unique().tolist()
    departements = df["nom_departement"].sort_values().unique() if 'nom_departement' in df.columns else []
    sous_prefectures = df["nom_sousprefecture"].sort_values().unique() if 'nom_sousprefecture' in df.columns else []

    return render_template('requete_indicateur.html', indicateurs=indicateurs, regions=regions, 
                           departements=departements, sous_prefectures=sous_prefectures)














if __name__ == '__main__':
    app.run(debug=True)
