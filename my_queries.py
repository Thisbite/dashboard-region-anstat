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
            cursor.execute("SELECT indicateur FROM indicateur_v2")
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



# Obtenir la définition associé à l'indicateur
# La fonction pour obtenir la définition en fonction de l'indicateur
def definition_indicateur(indicateur_choisi):
    try:
        with cf.create_connection() as conn:
            cursor = conn.cursor()
            # Requête pour obtenir la définition de l'indicateur choisi
            query = "SELECT definitions FROM indicateur_v2 WHERE indicateur = %s"
            cursor.execute(query, (indicateur_choisi,))
            # Récupérer le résultat
            result = cursor.fetchone()
            if result:
                return result[0]  # Retourne la définition si elle existe
            else:
                return f"Définition pour l'indicateur '{indicateur_choisi}' non trouvée."
    except Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Exception in definition_indicateur: {e}")
        return None


#Mode de calcul:
def mode_calcul_indicateur(mode_calcul):
    try:
        with cf.create_connection() as conn:
            cursor = conn.cursor()
            # Requête pour obtenir la définition de l'indicateur choisi
            query = "SELECT  mode_calcul FROM indicateur_v2 WHERE indicateur = %s"
            cursor.execute(query, (mode_calcul,))
            # Récupérer le résultat
            result = cursor.fetchone()
            if result:
                return result[0]  # Retourne la définition si elle existe
            else:
                return f"Mode de calcul pour l'indicateur '{mode_calcul}' non trouvée."
    except Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"Exception in definition_indicateur: {e}")
        return None



def get_data(filepath):
    df = pd.read_csv(filepath, sep=',')
    return df


def get_data_from_mysql():
    # Configurer les informations de connexion à la base de données MySQL
    conn = cf.create_connection()
    # Requête SQL pour sélectionner toutes les données
    query = "SELECT * FROM valeur_indicateur_libelle_ok"

    # Charger les données dans un DataFrame pandas
    df = pd.read_sql(query, conn)

    # Fermer la connexion
    conn.close()

    return df


