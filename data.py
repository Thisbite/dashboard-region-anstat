import folium
import json
import branca.colormap as cm  # Pour créer un dégradé de couleurs
from flask import Flask, render_template

app = Flask(__name__)

def statistiques():
    # Charger le fichier GeoJSON
    with open('static/carte/populations_ok.json', 'r') as f:
        geojson_data = json.load(f)

    # Créer la carte centrée sur la Côte d'Ivoire avec un fond blanc
    m = folium.Map(location=[7.539989, -5.547080], zoom_start=6, tiles=None)

    # Ajouter un fond de carte blanc
    folium.TileLayer(tiles="CartoDB Positron", name="Fond Blanc", control=False).add_to(m)

    # Extraire les populations et trouver les minimum et maximum pour l'échelle de couleur
    populations = [feature['properties']['Population'] for feature in geojson_data['features']]
    min_pop = min(populations)
    max_pop = max(populations)

    # Créer une échelle de couleur basée sur la population
    colormap = cm.LinearColormap(colors=['red', 'orange', 'lightgreen', 'green'], vmin=min_pop, vmax=max_pop)

    # Ajouter les polygones des régions à partir du GeoJSON avec les populations
    geojson_layer = folium.GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': colormap(feature['properties']['Population']),
            'color': 'black',  # Bordure des polygones
            'weight': 2,
            'fillOpacity': 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["REGION", "Population"],  # Champs à afficher dans le tooltip
            aliases=["Région: ", "Population: "],  # Les noms affichés pour chaque champ
            localize=True,
            sticky=True,
            labels=True,
            toLocaleString=True,
        )
    ).add_to(m)

    # Ajouter la légende avec un effet de clic
    colormap_html = colormap._repr_html_()
    legend_html = f'''
    <div id="legend" style="
                position: fixed;
                bottom: 10px;
                left: 40%;
                transform: translateX(-50%);
                z-index: 1000;
                background-color: rgba(255, 255, 255, 0.8);
                padding: 1px;
                border-radius: 8px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.4);
                cursor: pointer;">
    {colormap_html}
    </div>
    '''

    # Ajouter un titre en haut de la carte
    title_html = '''
         <div style="position: fixed; 
                     top: 1px; left: 50%; 
                     transform: translateX(-50%);
                     z-index: 1000;
                     background-color: white; 
                     padding: 10px;
                     font-size: 16px;
                     font-weight: bold;
                     border-radius: 8px;
                     box-shadow: 2px 2px 10px rgba(0,0,0,0.4);
                     ">
            Population selon les régions, 2021
         </div>
     '''

    # Ajouter l'image de la boussole (symbole du nord)
    compass_html = '''
         <div style="position: fixed; 
                     top: 50px; right: 50px; 
                     z-index: 1000;
                     width: 100px; 
                     height: 100px; 
                     background-image: url('https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Compass_rose_pale.svg/1024px-Compass_rose_pale.svg.png');
                     background-size: cover;
                     background-repeat: no-repeat;
                     ">
         </div>
     '''

    # Ajouter les éléments de la légende, du titre et de la boussole séparément
    m.get_root().html.add_child(folium.Element(legend_html))
    m.get_root().html.add_child(folium.Element(title_html))
    m.get_root().html.add_child(folium.Element(compass_html))

    # Ajouter un script JavaScript pour gérer les interactions
    script =  """
<script>
    // Fonction pour basculer la visibilité d'un polygone spécifique
    function togglePolygonByColor(color) {
        var geojsonLayers = document.getElementsByClassName('leaflet-interactive');
        for (var i = 0; i < geojsonLayers.length; i++) {
            var layer = geojsonLayers[i];
            if (layer.style.fill === color) {
                if (layer.style.opacity == "0") {
                    layer.style.opacity = "1";  // Rendre visible
                } else {
                    layer.style.opacity = "0";  // Rendre invisible
                }
            }
        }
    }

    // Ajouter un événement de clic à chaque couleur de la légende
    var colors = document.getElementsByClassName('legend-color');
    for (var j = 0; j < colors.length; j++) {
        colors[j].onclick = function() {
            var selectedColor = this.getAttribute('data-color');  // Récupérer la couleur associée
            togglePolygonByColor(selectedColor);  // Appeler la fonction pour cette couleur
        };
    }
</script>

    """

    m.get_root().html.add_child(folium.Element(script))

    # Sauvegarder la carte sous forme de chaîne HTML
    map_html = m._repr_html_()

    return map_html
