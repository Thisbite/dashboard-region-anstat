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
from io import StringIO




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



@app.route('/autocomplete_indicateur')
def autocomplete_indicateur():
    term = request.args.get('term', '')
    indicateurs_options = qr.options_indicateur()
    
    # Simuler une liste d'indicateurs (à remplacer par une vraie requête de base de données)
    indicateurs = indicateurs_options
    
    # Filtrer la liste en fonction du terme de recherche
    results = [{'label': ind, 'value': ind} for ind in indicateurs if term.lower() in ind.lower()]
    
    return jsonify(results)



# Obtenir la région en fonction de l'indicateur
@app.route('/get_regions', methods=['GET'])
def get_regions():
    indicateur = request.args.get('indicateur')
    df = qr.get_data_from_mysql()  # Récupère les données
    regions = df[df['indicateur'] == indicateur]['region'].dropna().sort_values().unique()
    return jsonify(list(regions))

# Route pour récupérer les départements en fonction de la région sélectionnée
@app.route('/get_departements', methods=['GET'])
def get_departements():
    region = request.args.get('region')
    df = qr.get_data_from_mysql()  # Récupère les données
    departements = df[df['region'] == region]['departement'].sort_values().unique()
    return jsonify(list(departements))

# Route pour récupérer les sous-préfectures en fonction du département sélectionné
@app.route('/get_sous_prefectures', methods=['GET'])
def get_sous_prefectures():
    departement = request.args.get('departement')
    df = qr.get_data_from_mysql()  # Récupère les données
    sous_prefectures = df[df['departement'] == departement]['sousprefecture'].sort_values().unique()
    return jsonify(list(sous_prefectures))

# Route pour afficher la page de requête
@app.route('/request_indicateur', methods=['GET', 'POST'])
def request_indicateur():
    # Charger les données depuis MySQL
    df = qr.get_data_from_mysql()
    indicateur2= request.args.get('indicateur2')

    # Obtenir les options pour chaque filtre (indicateur, région, etc.)
    indicateurs_options = qr.options_indicateur()
    print("Indicateur 2:", indicateur2)

    if request.method == 'POST':
        # Récupérer les sélections de l'utilisateur
        indicateur_SELECT = request.args.get('indicateur2')
        region_SELECT = request.form.get('region')
        departement_SELECT = request.form.get('departement')
        sousprefecture_SELECT = request.form.get('sous_prefecture')

        # Commencer avec l'ensemble complet des données, sans colonnes inutiles
        df_filtered = df.drop(columns=['statut_approbation', 'id'], errors='ignore')

        # Appliquer les filtres en fonction des sélections
        if indicateur_SELECT:
            df_filtered = df_filtered[df_filtered['indicateur'] == indicateur_SELECT]
            print("Indicateur sélectionné:", indicateur_SELECT)

        if region_SELECT:
            df_filtered = df_filtered[df_filtered['region'] == region_SELECT]
            print("Région sélectionnée:", region_SELECT)

        if departement_SELECT:
            df_filtered = df_filtered[df_filtered['departement'] == departement_SELECT]
            print("Département sélectionné:", departement_SELECT)

        if sousprefecture_SELECT:
            df_filtered = df_filtered[df_filtered['sousprefecture'] == sousprefecture_SELECT]
            # Supprimer les colonnes région et département si sous-préfecture est sélectionnée
            df_filtered = df_filtered.drop(columns=['region', 'departement'], errors='ignore')
            print("Sous-préfecture sélectionnée:", sousprefecture_SELECT)

        # Supprimer les colonnes contenant uniquement des NaN
        df_filtered = df_filtered.dropna(axis=1, how='all')
        print("DataFrame filtré avant suppression des NaN:\n", df_filtered)

        # Normaliser les valeurs de la colonne 'indicateur' pour éviter les erreurs d'espacement
        df_filtered['indicateur'] = df_filtered['indicateur'].str.strip().str.lower()

        # Vérifier si le DataFrame filtré est vide
        if df_filtered.empty:
            message = "Aucune donnée disponible pour les critères sélectionnés."
            return render_template('result.html', available_columns=[], message=message)
        else:
            # Après avoir filtré les données en fonction des critères de l'utilisateur
            print("Indicateur sélectionné:", indicateur_SELECT)
            print("Région sélectionnée:", region_SELECT)
            print("Département sélectionné:", departement_SELECT)
            print("Sous-préfecture sélectionnée:", sousprefecture_SELECT)
            
            

            print(df_filtered.head())  # Vérifie les premières lignes

            # Stocker le DataFrame filtré dans la session (au format JSON) avec StringIO pour éviter l'avertissement FutureWarning
            from io import StringIO
            df_filtered_json = StringIO()
            df_filtered.to_json(df_filtered_json)
            session['df_filtered'] = df_filtered_json.getvalue()

            # Obtenir les colonnes disponibles pour la zone de dépôt
            available_columns = list(df_filtered.columns)
            defintions=qr.definition_indicateur(indicateur_choisi=indicateur_SELECT)
            mode_calcul=qr.mode_calcul_indicateur(mode_calcul=indicateur_SELECT)
            print('defintions indicateur:',defintions)
            print('Mode de calcul:',mode_calcul)

            # Afficher la page résultat avec les colonnes disponibles,pour les elements dans la page résultat c'est ici
            return render_template('result.html', available_columns=available_columns, 
                                   indicateur_SELECT=indicateur_SELECT,
                                   defintions=defintions,
                                   mode_calcul=mode_calcul)

    # Si GET, afficher la page de sélection avec les options de filtre
    regions = df['region'].dropna().sort_values().unique()
    departements = df['departement'].dropna().sort_values().unique()
    sous_prefectures = df['sousprefecture'].dropna().sort_values().unique()

    return render_template(
        'requete_indicateur.html',
        indicateurs=indicateurs_options,
        regions=regions,
        departements=departements,
        sous_prefectures=sous_prefectures,
        indicateur2=indicateur2
    )




# Route pour générer le tableau croisé
@app.route('/generate_pivot_table', methods=['POST'])
def generate_pivot_table():
    data = request.get_json()
    selected_columns = data.get('columns', [])

    # Recharger le DataFrame filtré depuis la session
    df_filtered_json = session.get('df_filtered', None)

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
