Ce fichier README a été généré le 2023-09-01 par Merwan AMIMEUR

Dernière mise-à-jour le : 2023-09-01.

# INFORMATIONS GENERALES

## Données utilisées :
Données publiques du site USGS : https://www.usgs.gov/

## Adresse de contact :
 
merwan.amimeur@gmail.com

# INFORMATIONS METHODOLOGIQUES

## Objectif du projet : 

Ce projet a pour objectif de créer une version application d'un outil d'alerting en cas de tremblement de terre.
Il se découpe en deux volet :
 - Une option pour croiser une liste de coordonnées géographiques avec les tremblements de terre ayant eu lieu.
 - Une option pour observer un tremblement de terre en particulier et vérifier si un point se situe dans le périmètre d'impact de ce dernier.

## Description des sources et méthodes utilisées pour collecter et générer les données :
Les données sont récupérer automatiquement via des requêtes sur l'API du site USGS : 
https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time_str}&endtime={end_time_str}&minmmi={mmi}
Permettant de récupérer tous les tremblements de terre ayant un MMI >= mmi, et dans la période de temps définie entre start_time_str et end_time_str.

Par ailleurs, l'utilisateur peut lui-même uploader une liste de coordonnées géographiques afin de croiser avec les informations USGS.

## Méthodes de traitement des données :
Une fois les données des tremblements de terres récupérées depuis l'API USGS, et le fichier de l'utilisateur uploadé, le code traite les données en deux étapes :
1) Récupération des informations précises sur les impacts du tremblement de terre:
   	Récupération du grid.xml via une seconde requête sur l'API du site d'USGS sur l'évènement sélectionné par l'utilisateur.
   	Lien API pour l'évènement 'id' :https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&eventid={id}
3) Croisement entre les données du grid.xml et les coordonnées géographiques afin de déterminer quels sont les impacts précis sur les points observés.

## Autres informations contextuelles :
Les données étant récupérées automatiquement sur le site USGS, la précision et l'exhaustivité de la donnée est dépendante de la qualité des informations présentes sur ce site. 

# APERCUS DES DONNEES ET FICHIERS

## Convention de nommage des fichiers :
Le nom du fichier uploadé par l'utilisateur n'a pas d'importance.

# INFORMATIONS SPECIFIQUES AUX DONNEES POUR LE FICHIER UPLOADE PAR L'UTILISATEUR

## Liste des variables/entêtes de colonne :

Les informations sont les suivantes : 
Nom de la variable | Description | Format

 
	-- Nom | Nom du site observé | Caractère
	-- Entité | Nom de l'entité dans laquelle se trouve le site | Caractère
	-- Latitude | Latitude du site (coordonnée géographique) | float
	-- Longitude | Longitude du site (coordonnée géographique) | float
	-- TIV | Valeur assurée (Total Insured Value) | float


Toutes ces variables sont obligatoires.
