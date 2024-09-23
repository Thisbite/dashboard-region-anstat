from flask import Flask, render_template, request, redirect, url_for, flash, session,send_file
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

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

# Route pour récupérer les départements en fonction de la région sélectionnée
@app.route('/get_departements/<region>')
def get_departements(region):
    df = get_data("region_poro1.csv")  # Charger les données
    df_filtered = df[df['nom_region'] == region]
    departements = df_filtered['nom_departement'].sort_values().unique()
    return jsonify(list(departements))

# Route pour récupérer les sous-préfectures en fonction du département sélectionné
@app.route('/get_sous_prefectures/<departement>')
def get_sous_prefectures(departement):
    df = get_data("region_poro1.csv")  # Charger les données
    df_filtered = df[df['nom_departement'] == departement]
    sous_prefectures = df_filtered['nom_sousprefecture'].sort_values().unique()
    return jsonify(list(sous_prefectures))

# Route pour afficher la page de requête
@app.route('/request_indicateur', methods=['GET', 'POST'])
def request_indicateur():
    # Charger les données
    xpath = "region_poro1.csv"
    df = get_data(xpath)
    
    # Extraire les options disponibles pour chaque filtre
    indicateurs = df["nom_indicateur"].sort_values().unique()
    regions = df['nom_region'].sort_values().unique()
    departements = df['nom_departement'].sort_values().unique()
    sous_prefectures = df['nom_sousprefecture'].sort_values().unique()

    if request.method == 'POST':
        # Récupérer les sélections de l'utilisateur
        indicateur_SELECT = request.form.get('indicateur')
        region_SELECT = request.form.get('region')
        departement_SELECT = request.form.get('departement')
        sousprefecture_SELECT = request.form.get('sous_prefecture')

        # Commencer avec l'ensemble complet des données
        df_filtered = df.drop(columns=['statut','id'], errors='ignore')
        df_filtered =df_filtered[df_filtered['nom_indicateur'] == indicateur_SELECT]

        # Appliquer chaque filtre uniquement si une valeur est sélectionnée
        if sousprefecture_SELECT:
            df_filtered = df_filtered[df_filtered['nom_sousprefecture'] == sousprefecture_SELECT]
            # Supprimer les colonnes 'nom_region' et 'nom_departement' si la sous-préfecture est sélectionnée
            df_filtered = df_filtered.drop(columns=['nom_region', 'nom_departement'], errors='ignore')
        # Si le département est sélectionné (et pas de sous-préfecture), on filtre par département
# et on supprime la colonne région
        elif departement_SELECT and not sousprefecture_SELECT:
            df_filtered = df_filtered[
                (df_filtered['nom_region'] == region_SELECT) &
                (df_filtered['nom_departement'].isna()) 

            ]
            
            # Supprimer la colonne 'nom_region' si le département est sélectionné
            df_filtered = df_filtered.drop(columns=['nom_region'], errors='ignore')
        elif region_SELECT and not departement_SELECT and not sousprefecture_SELECT:
            df_filtered = df_filtered[
                (df_filtered['nom_region'] == region_SELECT) &
                (df_filtered['nom_departement'].isna()) &
                (df_filtered['nom_sousprefecture'].isna())
            ]


        # Supprimer les colonnes contenant uniquement des valeurs NaN
        df_filtered = df_filtered.dropna(axis=1, how='all')

        # Vérifier si le DataFrame filtré est vide
        if df_filtered.empty:
            # Si aucun résultat n'est trouvé, renvoyer un message "Aucune donnée disponible"
            message = "Aucune donnée disponible pour les critères sélectionnés."
            return render_template('result.html', available_columns=[], message=message)
        else:
            # Stocker le DataFrame filtré dans la session (au format JSON)
            session['df_filtered'] = df_filtered.to_json()

            # Obtenir les colonnes disponibles pour la zone de dépôt
            available_columns = list(df_filtered.columns)
        

            # Afficher la page résultat avec les colonnes disponibles et sans message d'erreur
            return render_template('result.html', available_columns=available_columns, message="",indicateur_SELECT=indicateur_SELECT)

    # Si GET, afficher la page de sélection avec les options de filtre
    return render_template(
        'requete_indicateur.html', 
        indicateurs=indicateurs, 
        regions=regions, 
        departements=departements, 
        sous_prefectures=sous_prefectures
    )


# Route pour générer le tableau croisé
@app.route('/generate_pivot_table', methods=['POST'])
def generate_pivot_table():
    data = request.get_json()
    selected_columns = data.get('columns', [])
    

    # Reload filtered dataframe from session
    df_filtered_json = session.get('df_filtered', None)

    if df_filtered_json:
        df = pd.read_json(df_filtered_json)
        
        if selected_columns:
            # Generate the pivot table based on selected columns
            pivot_table = pd.pivot_table(df, values='Valeur', index=selected_columns,aggfunc='sum')
            pivot_html = pivot_table.to_html(classes='table table-bordered')

            return jsonify({"table_html": pivot_html})

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
        pivot_table = pd.pivot_table(df, values='Valeur', index=selected_columns, aggfunc='sum')

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






if __name__ == '__main__':
    app.run(debug=True)
