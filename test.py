from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

# Route pour afficher la page HTML (index)
@app.route('/')
def index():
    min_year = 2019
    max_year = 2027
    return render_template('test.html', min=min_year, max=max_year)








# Route pour servir les données en format JSON
@app.route('/data')
def get_data():
    data = []
    
    # Générer les données pour l'indicateur "Production de cultures"
    cultures = ['Cacao', 'Café', 'Coton']
    annees = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027]

    for annee in annees:
        for culture in cultures:
            data.append({
                'indicateur': 'Production',
                'produit': culture,
                'annee': annee,
                'valeur': random.randint(1000, 5000)  # Production en tonnes, valeur aléatoire
            })
            
    # Générer les données pour l'indicateur "Effectif de la population"
    sexes = ['M', 'F']
    groupes_age = ['0-4', '5-9', '10-14', '15-19', '20-24']

    for annee in annees:
        for sexe in sexes:
            for groupe in groupes_age:
                data.append({
                    'indicateur': 'Effectif de la population',
                    'annee': annee,
                    'sexe': sexe,
                    'groupe_age': groupe,
                    'valeur': random.randint(50000, 150000)  # Génération aléatoire d'effectif
                })
    
    # Générer les données pour un autre indicateur "Effectif de la population 1"
    for annee in annees:
        for sexe in sexes:
            data.append({
                'indicateur': 'Effectif de la population1',
                'annee': annee,
                'sexe': sexe,
                'valeur': random.randint(1000000, 8000000)  # Génération aléatoire d'effectif
            })
            
    #Generer le taux de mortalité

    zones= ['Régional','National']

    for annee in annees:
 
        for zone in zones:
            data.append({
                'indicateur': 'Taux de mortalité',
                'annee': annee,
                'zone':zone,
                'valeur': round(random.uniform(60, 100), 2)  # Taux entre 60% et 100%
            })
            
            
    # Générer les données pour le taux de pauvreté
    zones = ['Régional','National']
    
    for annee in annees:
        for zone in zones:
            data.append({
                'indicateur': 'Taux de pauvreté',
                'annee': annee,
                'zone': zone,
                'valeur': round(random.uniform(0, 100), 2)  # Taux entre 0% et 100%
            })
                
    # Générer les données pour l'indicateur "Taux de scolarisation"
    cycles_scolaires = ['préscolaire', 'primaire', 'secondaire 1er cycle', 'secondaire 2ème cycle']

    for annee in annees:
        for sexe in sexes:
            for cycle in cycles_scolaires:
                data.append({
                    'indicateur': 'Taux de scolarisation',
                    'annee': annee,
                    'sexe': sexe,
                    'cycle_scolaire': cycle,
                    'valeur': round(random.uniform(60, 100), 2)  # Taux entre 60% et 100%
                })

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
