import pyodbc # type: ignore
from flask import Flask, redirect, render_template, request, url_for # type: ignore

app = Flask(__name__)

# Azure SQL Database Connection
server = 'serveur-societe.database.windows.net'  # Replace with your server name
database = 'societe'  # Replace with your database name
username = 'societe'  # Replace with your username
password = 'Dawser12345'  # Replace with your password
driver = '{ODBC Driver 18 for SQL Server}'  # Ensure this is correct

# Corrected Connection String
conn = pyodbc.connect(
    f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
)

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

if __name__ == '__main__':
    app.run(debug=True)
