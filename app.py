from flask import Flask, render_template, request, redirect, url_for, flash, session
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

# Route pour afficher la page de requête
@app.route('/request_indicateur', methods=['GET', 'POST'])
def request_indicateur():
    # Load the data
    xpath = "region_poro1.csv"
    df = get_data(xpath)
    indicateurs = df["nom_indicateur"].sort_values().unique()

    if request.method == 'POST':
        indicateur_SELECT = request.form.get('indicateur')

        if indicateur_SELECT:
            # Filter the data based on the selected indicator
            df_filtered = df[df['nom_indicateur'] == indicateur_SELECT]
            
            # Drop columns where all values are NaN
            df_filtered = df_filtered.dropna(axis=1, how='all')

            # Store filtered dataframe in session as JSON string
            session['df_filtered'] = df_filtered.to_json()

            # Get available columns for drag and drop
            available_columns = list(df_filtered.columns)
            return render_template('result.html', available_columns=available_columns)

    return render_template('requete_indicateur.html', indicateurs=indicateurs)

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
            pivot_table = pd.pivot_table(df, values='Valeur', index=selected_columns, aggfunc='sum')
            pivot_html = pivot_table.to_html(classes='table table-bordered')

            return jsonify({"table_html": pivot_html})

    return jsonify({"table_html": "<p>Aucune colonne sélectionnée</p>"})














if __name__ == '__main__':
    app.run(debug=True)
