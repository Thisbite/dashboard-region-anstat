import pandas as pd
import mysql.connector
import config as cf

# 1. Lecture du fichier Excel avec pandas
file_path = "data_indicateur.xlsx"  # Remplacez avec le chemin de votre fichier Excel
df = pd.read_excel(file_path)

# 2. Connexion à la base de données MySQL
connection =cf.create_connection()

cursor = connection.cursor()

# 3. Insertion des données dans la table 'indicateur_v2'
insert_query = """
INSERT INTO indicateur_v2 (indicateur_id, indicateur, definitions, mode_calcul)
VALUES (%s, %s, %s, %s)
"""

for _, row in df.iterrows():
    # Utilisez les colonnes de l'Excel pour insérer les valeurs dans la table
    data = (row['id'], row['Indicateurs'], row['Definition de l\'indicateur'], row['Mode de calcul'])
    cursor.execute(insert_query, data)

# 4. Valider les changements et fermer la connexion
connection.commit()
cursor.close()
connection.close()

print("Les données ont été insérées avec succès.")
