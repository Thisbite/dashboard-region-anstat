from mysql.connector import Error
import config as cf 
import pandas as pd

def options_regions():
    try:
        with cf.create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nom_region FROM Region")
            # Récupérer les résultats sous forme de liste de tuples
            regions = cursor.fetchall()
    except Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Exception in options_regions: {e}")
        return []
    
    regions=[row[0] for row in regions]
    return regions



#  La liste des indicateurs
def options_indicateur():
    try:
        with cf.create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nom_indicateur FROM Indicateur")
            # Récupérer les résultats sous forme de liste de tuples
            indicateurs = cursor.fetchall()
    except Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Exception in options_regions: {e}")
        return []
    
    indicateurs =[row[0] for row in indicateurs ]
    return indicateurs 

def get_data(filepath):
    df = pd.read_csv(filepath, sep=',')
    return df


