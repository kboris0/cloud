import os
import pyodbc # type: ignore
from flask import Flask, redirect, render_template, request, url_for # type: ignore

app = Flask(__name__)

# Récupérer les informations de connexion depuis les variables d'environnement
server = os.getenv('DB_SERVER', 'societe.database.windows.net')  # Nom du serveur Azure
database = os.getenv('DB_NAME', 'societe')  # Nom de la base de données
username = os.getenv('DB_USER', 'societe')  # Nom d'utilisateur
password = os.getenv('DB_PASSWORD', 'Dawser1234')  # Mot de passe
driver = '{ODBC Driver 18 for SQL Server}'  # S'assurer que le driver est installé

# Chaîne de connexion à la base de données Azure
conn_str = (
    f'Driver={driver};'
    f'Server=tcp:{server},1433;'
    f'Database={database};'
    f'Uid={username};'
    f'Pwd={password};'
    f'Encrypt=yes;'
    f'TrustServerCertificate=no;'
    f'Connection Timeout=30;'
)
conn = pyodbc.connect(conn_str)


# Routes
@app.route('/')
def home():
    return redirect(url_for('list_clients'))

@app.route('/ajout_client', methods=['GET', 'POST'])
def ajout_client():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        age = request.form['age']
        id_region = request.form['id_region']

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO client (nom, prenom, age, ID_region) 
                VALUES (?, ?, ?, ?)
            """, (nom, prenom, age, id_region))
            conn.commit()
        return redirect(url_for('list_clients'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT ID_region, libelle FROM region")
        regions = cursor.fetchall()
    return render_template('ajout_client.html', regions=regions)

@app.route('/liste_client')
def list_clients():
    with conn.cursor() as cursor:
        cursor.execute("""
            select c.ID_client, c.nom, c.prenom , c.age, r.libelle 
                       from client c,region r where c.ID_region=r.ID_region
        """)
        clients = cursor.fetchall()
    return render_template('liste_client.html', clients=clients)

@app.route('/liste_region')
def list_regions():
    with conn.cursor() as cursor:
        cursor.execute("""
SELECT * FROM region;        """)
        regions = cursor.fetchall()
    return render_template('list-region.html', regions=regions)
@app.route('/supprimer/<int:id_client>')
def supprimer(id_client):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM client WHERE ID_client = ?", (id_client,))
        conn.commit()
    return redirect(url_for('list_clients'))

@app.route('/modifier/<int:id_client>', methods=['GET', 'POST'])
def modifier(id_client):
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        age = request.form['age']
        id_region = request.form['id_region']

        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE client 
                SET nom = ?, prenom = ?, age = ?, ID_region = ? 
                WHERE ID_client = ?
            """, (nom, prenom, age, id_region, id_client))
            conn.commit()
        return redirect(url_for('list_clients'))

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM client WHERE ID_client = ?", (id_client,))
        client = cursor.fetchone()
        cursor.execute("SELECT ID_region, libelle FROM region")
        regions = cursor.fetchall()
    return render_template('modifier.html', client=client, regions=regions)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
