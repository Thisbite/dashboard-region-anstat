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
import io



import folium
import json
# On a une liste sur les régions de la CI, en effet elle est la page principale


from flask import render_template

import branca.colormap as cm 
import random
import time
from datetime import datetime





app = Flask(__name__)
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




# Fichier pour stocker les données sur l'horloge de population
STORAGE_FILE = 'births_data.json'

# Date de départ pour le calcul des naissances (exemple : 1er janvier 2022)
START_DATE = datetime(2022, 1, 1)

# Fonction pour calculer les naissances par seconde avec variation
def get_births_per_second():
    moyenne_naissance = 10
    variation = random.uniform(-0.034, 0.034)
    return round(moyenne_naissance, 2)

# Fonction pour charger l'état actuel du compteur
def load_birth_data():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            data = json.load(f)
            return data
    # Si le fichier n'existe pas, on retourne un total de naissances par défaut et la date de départ
    return {'total_births':29090897, 'last_time': START_DATE.timestamp()}

# Fonction pour sauvegarder l'état actuel du compteur
def save_birth_data(total_births, last_time):
    data = {'total_births': total_births, 'last_time': last_time}
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f)

# Fonction pour calculer les naissances accumulées depuis une date de départ
def calculate_accumulated_births():
    birth_data = load_birth_data()
    last_time = birth_data['last_time']
    total_births = birth_data['total_births']

    # Temps écoulé depuis la date de départ ou la dernière mise à jour (en secondes)
    current_time = time.time()
    elapsed_time = current_time - last_time

    # Calculer les naissances accumulées pendant ce temps
    births_per_second = get_births_per_second()
    accumulated_births = births_per_second * elapsed_time

    # Mettre à jour le total des naissances
    total_births += accumulated_births

    # Sauvegarder le nouvel état
    save_birth_data(total_births, current_time)

    return total_births

@app.route('/naissance')
def naissance():
    return render_template('naissance.html')

@app.route('/births_data')
def births_data():
    # Calculer les naissances accumulées
    total_births = calculate_accumulated_births()

    # Obtenir la date et l'heure actuelles
    now = datetime.now()
    
    # Extraire le jour, le mois et l'année
    day = now.day
    month = now.month
    year = now.year

    # Renvoie les données en JSON pour le frontend
    data = {
        'time': time.time(),
        'total_births': round(total_births, 2),
        'births_per_second': get_births_per_second(),
        'day': day,
        'month': month,
        'year': year
    }
    return jsonify(data)



















@app.route('/dashboard')
def dashboard():
    # Définir les années de 2018 à 2024
    region = request.args.get('region', session.get('region', 'DefaultRegion'))
    min_year = 2018
    max_year = 2024
    annees = list(range(min_year, max_year + 1))
    sexes = ['M', 'F']

    data = { 'M': [], 'F': [] }
    data_coton = []
    
    # Générer les données pour chaque année et sexe pour la région sélectionnée
    for sexe in sexes:
        for annee in annees:
            total_population = random.randint(50000, 1000000)
            data[sexe].append({'annee': annee, 'valeur': total_population})
            
    # Générer les données du coton pour chaque année
    for annee in annees:
        total_population = random.randint(50000, 1000000)
        data_coton.append(total_population)
    
    return render_template('pages/dashboard.html', region=region, data=data, annees=annees, data_coton=data_coton)


#Fiche synoptique
@app.route('/fiche-synoptique')
def fiche_synoptique():
     # Définir les années de 2018 à 2024
    region = request.args.get('region', session.get('region'))
    
    if region is None:
        return "Veuillez choisir une région.", 400
    return render_template('pages/notifications.html',region=region)
    










































@app.route('/statistiques')
def statistiques():
    # Charger le fichier GeoJSON
    with open('static/carte/populations_ok.json', 'r') as f:
        geojson_data = json.load(f)

    # Extraire les noms des régions et les populations
    regions = [feature['properties']['REGION'] for feature in geojson_data['features']]
    populations = [feature['properties']['Population'] for feature in geojson_data['features']]

    # Créer la carte centrée sur la Côte d'Ivoire
    m = folium.Map(location=[7.539989, -5.547080], zoom_start=6)

    # Créer une échelle de couleur basée sur la population
    colormap = cm.LinearColormap(colors=['red', 'orange', 'yellow', 'green', 'blue'], vmin=min(populations), vmax=max(populations))

    # Ajouter les polygones des régions à partir du GeoJSON avec les populations
    folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': colormap(feature['properties']['Population']),
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["REGION", "Population"],
            aliases=["Région: ", "Population: "],
            localize=True
        )
    ).add_to(m)

    # Ajouter la légende
    colormap.add_to(m)

    # Sauvegarder la carte sous forme de chaîne HTML
    map_html = m._repr_html_()

    # Renvoyer les données à la page HTML
    return render_template('statistiques.html', map_html=map_html, regions=regions, populations=populations)













@app.route('/')
def list_regions():
    regions = qr.options_regions()
    map_html = dt.statistiques()
    coord_list=[]
    # Données
    years = [2019, 2020, 2021, 2022, 2023]
    population = [24.0, 27.0, 27.4, 29.8, 30.38]
    school_enrollment_rate = [75, 76, 78, 79, 80]
    age_groups = ['0-14 ans', '15-24 ans', '25-54 ans', '55 - 59 ans','60 -64 ','65-69','70-74 ans']
    age_distribution = [40, 20, 30, 10, 18, 20]

    return render_template('home.html',
                           coord_list=coord_list,
                           years=years,
                           population=population,
                           school_enrollment_rate=school_enrollment_rate,
                           age_groups=age_groups,
                           age_distribution=age_distribution,
                           regions=regions,
                           map_html=map_html )




#Affichage de pdf
@app.route('/region/<region>')
def show_region_pdf(region):
    pdf_path = f"static/pdfs/{region}.pdf"  # Chemin vers le fichier PDF
    try:
        return render_template('region_pdf.html', region=region)
    except FileNotFoundError:
        return f"PDF pour la région {region} non trouvé.", 404




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

@app.route('/request_indicateur', methods=['GET', 'POST'])
def request_indicateur():
    # Charger les données depuis MySQL
    df = qr.get_data_from_mysql()

    # Récupérer l'indicateur passé en paramètre dans l'URL
    indicateur2 = request.args.get('indicateur2')

    # Obtenir les options pour chaque filtre (indicateur, région, etc.)
    indicateurs_options = qr.options_indicateur()
    print("Indicateur 2:", indicateur2)

    if request.method == 'POST':
        # Récupérer les sélections de l'utilisateur
        indicateur_SELECT = request.args.get('indicateur2')  # ou request.form.get selon ton besoin
        region_SELECT = request.form.get('region')
        departement_SELECT = request.form.get('departement')
        sousprefecture_SELECT = request.form.get('sous_prefecture')

        # Commencer avec l'ensemble complet des données
        df_filtered = df.drop(columns=['statut_approbation', 'id'], errors='ignore')

        # Appliquer les filtres en fonction des sélections
        if indicateur_SELECT and 'indicateur' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['indicateur'].str.strip().str.lower() == indicateur_SELECT.strip().lower()]
            print("Indicateur sélectionné:", indicateur_SELECT)

        if not df_filtered.empty and region_SELECT and 'region' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['region'] == region_SELECT]
            print("Région sélectionnée:", region_SELECT)

        if not df_filtered.empty and departement_SELECT and 'departement' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['departement'] == departement_SELECT]
            print("Département sélectionné:", departement_SELECT)

        if not df_filtered.empty and sousprefecture_SELECT and 'sousprefecture' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['sousprefecture'] == sousprefecture_SELECT]
            df_filtered = df_filtered.drop(columns=['region', 'departement'], errors='ignore')
            print("Sous-préfecture sélectionnée:", sousprefecture_SELECT)

        # Supprimer les colonnes contenant uniquement des NaN
        df_filtered = df_filtered.dropna(axis=1, how='all')
        print("DataFrame filtré avant suppression des NaN:\n", df_filtered)

        # Vérifier si le DataFrame filtré est vide
        if df_filtered.empty:
            message = "Aucune donnée disponible pour les critères sélectionnés."
            return render_template('result.html', available_columns=[], message=message)
        
        # Si le DataFrame contient des données, normaliser les valeurs de la colonne 'indicateur'
        if 'indicateur' in df_filtered.columns:
            df_filtered['indicateur'] = df_filtered['indicateur'].str.strip().str.lower()
            print(df_filtered.head())

        # Vérifier si le DataFrame filtré est vide après toutes les opérations
        if df_filtered.empty:
            message = "Aucune donnée disponible après le filtrage."
            return render_template('result.html', available_columns=[], message=message)
        else:
            # Afficher les données filtrées
            print(df_filtered.head())

            # Stocker le DataFrame filtré dans la session au format JSON
            from io import StringIO
            df_filtered_json = StringIO()
            df_filtered.to_json(df_filtered_json)
            session['df_filtered'] = df_filtered_json.getvalue()

            # Obtenir les colonnes disponibles pour la zone de dépôt
            available_columns = list(df_filtered.columns)
            defintions = qr.definition_indicateur(indicateur_choisi=indicateur_SELECT)
            mode_calcul = qr.mode_calcul_indicateur(mode_calcul=indicateur_SELECT)

            print('Définitions de l\'indicateur:', defintions)
            print('Mode de calcul:', mode_calcul)

            # Afficher la page résultat avec les colonnes disponibles
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
        pivot_table = pd.pivot_table(df, index=selected_columns)

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

#==============================================================Domaine
#Section de domaine
@app.route('/domaines', methods=['GET', 'POST'])
def domaines():
    return render_template('domaines.html')


#Requete domaine

@app.route('/domaines_indicateur', methods=['GET', 'POST'])
def domaines_indicateur():
    df = qr.get_data_from_mysql()
    indicateurs_options = qr.options_indicateur()

    if request.method == 'POST':
        # Récupérer les sélections de l'utilisateur
        indicateur_SELECT = request.form.get('indicateur')
        region_SELECT = request.form.get('region')
        departement_SELECT = request.form.get('departement')
        sousprefecture_SELECT = request.form.get('sous_prefecture')

        # Commencer avec l'ensemble complet des données
        df_filtered = df.drop(columns=['statut_approbation', 'id'], errors='ignore')

        # Filtrer par indicateur
        if indicateur_SELECT and 'indicateur' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['indicateur'].str.strip().str.lower() == indicateur_SELECT.strip().lower()]
            print("Indicateur sélectionné:", indicateur_SELECT)

        # Filtrer par région
        if not df_filtered.empty and region_SELECT and 'region' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['region'] == region_SELECT]
            print("Région sélectionnée:", region_SELECT)

        # Filtrer par département
        if not df_filtered.empty and departement_SELECT and 'departement' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['departement'] == departement_SELECT]
            print("Département sélectionné:", departement_SELECT)

        # Filtrer par sous-préfecture
        if not df_filtered.empty and sousprefecture_SELECT and 'sousprefecture' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['sousprefecture'] == sousprefecture_SELECT]
            df_filtered = df_filtered.drop(columns=['region', 'departement'], errors='ignore')
            print("Sous-préfecture sélectionnée:", sousprefecture_SELECT)

        # Supprimer les colonnes contenant uniquement des NaN
        df_filtered = df_filtered.dropna(axis=1, how='all')

        # Vérifier si le DataFrame est vide après filtrage
        if df_filtered.empty:
            message = "Aucune donnée disponible pour les critères sélectionnés."
            return render_template('result.html', available_columns=[], message=message)

        # Stocker le DataFrame dans la session
        from io import StringIO
        df_filtered_json = StringIO()
        df_filtered.to_json(df_filtered_json)
        session['df_filtered'] = df_filtered_json.getvalue()

        # Récupérer les colonnes disponibles
        available_columns = list(df_filtered.columns)
        defintions = qr.definition_indicateur(indicateur_choisi=indicateur_SELECT)
        mode_calcul = qr.mode_calcul_indicateur(mode_calcul=indicateur_SELECT)

        return render_template('result.html', available_columns=available_columns,
                               indicateur_SELECT=indicateur_SELECT,
                               defintions=defintions,
                               mode_calcul=mode_calcul)


    # Si GET, afficher la page de sélection avec les options de filtre
    regions = df['region'].dropna().sort_values().unique()
    departements = df['departement'].dropna().sort_values().unique()
    sous_prefectures = df['sousprefecture'].dropna().sort_values().unique()

    return render_template(
        'domaines_indicateur.html',
        indicateurs=indicateurs_options,
        regions=regions,
        departements=departements,
        sous_prefectures=sous_prefectures
    )




#Fin du das bord avec les régions de la CI

if __name__ == '__main__':
    app.run(debug=True)
