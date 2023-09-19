import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import xml.etree.ElementTree as ET
import os
import folium
import requests
from datetime import datetime, timedelta
import json
import matplotlib
from scipy.spatial.distance import cdist
import openpyxl
import matplotlib.pyplot as plt
import numpy as np
import io
from fpdf import FPDF
import tempfile
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from bs4 import BeautifulSoup


def load_data(file):
    data = pd.read_csv(file,sep=',') if file.name.endswith('.csv') else pd.read_excel(file, engine='openpyxl')
    return data


# Fonction pour parser le fichier XML et obtenir le DataFrame
def parse_file_grid_xml(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    data = []

    for grid_data in root.findall('.//{http://earthquake.usgs.gov/eqcenter/shakemap}grid_data'):
        for point in grid_data.text.strip().split('\n'):
            values = point.split()
            lon, lat, mmi_value = map(float, values[:3])
            data.append((lon, lat, mmi_value))

    df = pd.DataFrame(data, columns=['Longitude', 'Latitude', 'MMI'])
    return df

def parse_link_grid_xml(lien_grid_xml,proxies=None):
    try:
        # Télécharger le contenu du lien
        response = requests.get(lien_grid_xml,proxies=proxies)
        response.raise_for_status()  # Lève une exception si la requête échoue

        contenu_xml = response.content

        # Définir les noms d'espace
        namespaces = {
            'ns': 'http://earthquake.usgs.gov/eqcenter/shakemap'
        }

        # Analyser le contenu XML
        root = ET.fromstring(contenu_xml)

        # Initialiser une liste pour stocker les données
        data = []

        # Parcourir et extraire les données
        for grid_data in root.findall('.//ns:grid_data', namespaces):
            for point in grid_data.text.strip().split('\n'):
                values = point.split()
                lon, lat, mmi_value = map(float, values[:3])
                data.append((lon, lat, mmi_value))

        # Créer un DataFrame
        df = pd.DataFrame(data, columns=['Longitude', 'Latitude', 'MMI'])

        return df
    except requests.exceptions.RequestException as e:
        print("Une erreur de requête s'est produite:", e)
        return None
    
def point_plus_proche(liste,grid):
    liste_mmi=[]
    for lat, lon in liste:
        lat0 = lat
        lon0 = lon

        #Borne du rectangle décrit dans le grid.xml
        lat_min, lat_max = grid["Latitude"].min(), grid["Latitude"].max()
        lon_min, lon_max = grid["Longitude"].min(), grid["Longitude"].max()
        
        # Rétrecicement de l'espace de recherche
        lat_floor, lat_roof = lat0-0.5,lat0+0.5
        lon_floor, lon_roof = lon0-0.5,lon0+0.5
        
        # Filtrage des points de la grille qui sont à l'intérieur du carré
        filtered_grid = grid[
            (grid['Latitude'] >= lat_floor) & (grid['Latitude'] <= lat_roof) &
            (grid['Longitude'] >= lon_floor) & (grid['Longitude'] <= lon_roof)
        ]
        
        if lat_min <= lat0 <= lat_max and lon_min <= lon0 <= lon_max:
            distance = cdist([(lat0, lon0)], filtered_grid[['Latitude', 'Longitude']], metric='euclidean')[0]
            index_plus_proche = filtered_grid.iloc[distance.argmin()].name
            mmi_value = filtered_grid.loc[index_plus_proche, 'MMI']
            
            liste_mmi.append(mmi_value)
        
        else:
            liste_mmi.append(0)
    return liste_mmi


def link_xml_event(id, proxies=None):
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&eventid={id}"
    try:
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()  # Lève une exception si la requête échoue
        data = response.json()  # Convertir la réponse JSON en dictionnaire

        # Accéder aux informations nécessaires dans la structure JSON
        url = data.get('properties', {}).get('products', {}).get('shakemap', [{}])[0].get('contents', {}).get('download/grid.xml', {}).get('url', None)
        title=json.loads(response.text)['properties']["place"]
        time=json.loads(response.text)['properties']["time"]
        mag=json.loads(response.text)['properties']["mag"]
        mmi=json.loads(response.text)['properties']["mmi"]
        return url,title,time,mag,mmi
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        return None


def download_list_event(period,mmi=0):

    period = int(period)

    # Obtenir la date et l'heure actuelles
    current_datetime = datetime.now()

    # Calculer la starttime en soustrayant la période de jours
    start_datetime = current_datetime - timedelta(days=period)

    # Convertir les objets datetime en chaînes de format AAAA-MM-JJTHH-MM-SS
    start_time_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = current_datetime.strftime('%Y-%m-%dT%H:%M:%S')

    if period>0:
        response = requests.get(f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time_str}&endtime={end_time_str}&minmmi={mmi}")
    else:
        response = requests.get(f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=1900-01-01&minmmi=4")
    data = json.loads(response.text)
    df_event = pd.json_normalize(data["features"])

    return df_event

def extract_table_data(html_content):
    # Analyser le HTML avec BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extraire les données du tableau
    table_data = []
    for row in soup.find_all('tr'):
        cell_data = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
        table_data.append(cell_data)

    return table_data

def calculate_font_size(col_width):
    # Ajustez ces valeurs selon vos besoins
    base_font_size = 10
    max_font_size = 40

    # Calculez la taille de la police en fonction de la largeur de la colonne
    font_size = base_font_size * (col_width / 80)  # 80 est la largeur de référence

    # Assurez-vous que la taille de la police ne dépasse pas la taille maximale
    return min(font_size, max_font_size)


def generate_pdf(html_content):
    # Créez un objet BytesIO pour stocker le PDF en mémoire
    pdf_buffer = BytesIO()

    # Créez le document PDF
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    story = []

    # Extraire les données du tableau
    table_data = extract_table_data(html_content)

    num_cols = len(table_data[0])
    col_widths = [150/num_cols] * num_cols

    # Créez un objet Table à partir des données du tableau
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), (0.9, 0.9, 0.9)),
                               ('GRID', (0, 0), (-1, -1), 1, (0.2, 0.2, 0.2))]))

    for i, col_width in enumerate(col_widths):
        font_size = calculate_font_size(col_width)
        table.setStyle(TableStyle([('FONT', (i, 0), (i, -1), 'Helvetica', font_size)]))

    # Ajoutez la table au PDF
    story.append(table)

    # Construisez le PDF
    doc.build(story)

    # Retournez les données du PDF
    pdf_buffer.seek(0)
    return pdf_buffer.read()

