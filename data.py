import folium
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

# Données des populations par région
data = {
    "Région": ["ABIDJAN", "YAMOUSSOUKRO", "GBOKLE", "NAWA", "SAN-PEDRO", "MORONOU", "INDENIE-DJUABLIN", 
               "SUD-COMOE", "FOLON", "KABADOUGOU", "LÔH-DJIBOUA", "GÔH", "HAUT-SASSANDRA", "MARAHOUE", 
               "IFFOU", "N'ZI", "BELIER", "GRAND-PONTS", "LA ME", "AGNEBY-TIASSA", "CAVALLY", "GUEMON", 
               "TONKPI", "BAGOUE", "PORO", "TCHOLOGO", "GBEKE", "HAMBOL", "BAFING", "BERE", "WORODOUGOU", 
               "BOUNKANI", "GONTOUGO"],
    "Population": [12500000, 899979, 6490683, 7988845, 4630304, 7598772, 7422276, 1841184, 6217205, 398521, 
                   
                   5991578, 7320220, 5939295, 3797283, 2816877, 1928909, 6548123, 6375140, 5117012, 7845053, 
                   
                   3894431, 3057754, 623680, 833095, 7330680, 7437080, 2830476, 7632489, 4955423, 7644161, 
                   7469850, 1659100, 4428778],
    
    "Latitude": [5.30966, 6.8180, 4.9487, 5.8786, 4.7486, 6.4497, 6.1364, 5.1463, 10.3787, 9.5807, 
                 6.3819, 6.1456, 7.3928, 7.2557, 7.3595, 7.1815, 6.9094, 5.4043, 5.7663, 5.6726, 
                 6.6179, 7.0396, 7.4748, 9.5632, 9.6562, 9.5122, 7.6716, 8.4028, 9.2754, 8.2904, 
                 8.5885, 9.5753, 8.0159],
    "Longitude": [-4.01266, -5.2767, -6.2629, -6.5644, -6.6422, -3.9094, -3.2070, -3.2051, -7.6594, -6.5933, 
                  -5.4093, -6.0028, -6.4894, -5.8147, -3.8030, -5.9051, -5.3090, -4.3464, -3.5287, -4.1719, 
                  -7.3465, -7.4184, -7.6232, -6.7175, -5.7891, -5.5112, -5.3397, -5.5608, -7.7933, -6.0717, 
                  -2.8713, -3.1944, -3.0081]
}



def statistiques():
    # Créer un DataFrame
    df = pd.DataFrame(data)

    # Créer la carte centrée sur la Côte d'Ivoire
    m = folium.Map(location=[7.539989, -5.547080], zoom_start=6)

    # Ajouter des cercles pour chaque région
    for i, row in df.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=row["Population"] / 1000000,  # Ajuster la taille du cercle en fonction de la population
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=1,
            popup=f"{row['Région']}: {row['Population']}",# Quand on survol on peut faire la lecture
            tooltip=f"Population: {row['Population']} \n  Région:{row['Région']}" 
        ).add_to(m)
        
        title_html = '''
         <div style="position: fixed; 
         bottom: 5px; left: 5px; width: 300px; height: auto; 
         background-color: white; z-index:9999; font-size:14px; padding: 10px;
         border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
         Répartition de la population<br>par région de la Côte d'Ivoire (2021)
         </div>
         '''

         
    m.get_root().html.add_child(folium.Element(title_html))

    # Sauvegarder la carte sous forme de chaîne HTML
    map_html = m._repr_html_()
    
    return map_html