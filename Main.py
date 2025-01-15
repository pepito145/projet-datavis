from flask import Flask, render_template, request, jsonify, redirect, session,  url_for, jsonify
import pandas as pd
import re
from re import search
import csv
import os

import plotly.graph_objs as go
import plotly

app = Flask(__name__)
app.secret_key= "pokemon" 

app.config['TEMPLATES_AUTO_RELOAD'] = True
query=""
types =[]
counters = {}

# Lecture des objets depuis un fichier CSV
def read_objects_from_csv(file_path):
	objects = []
	
	with open(file_path, 'r', encoding='utf-8-sig') as file:
		# Lecture des en-têtes de colonnes
		headers = file.readline().strip().split(';')
		
		# Lecture des lignes de données
		for line in file:
			values = line.strip().split(';')
			obj = dict(zip(headers, values))
			objects.append(obj)
	
	return objects


# Creation des listes des pokemons et des lieux
pokemons = read_objects_from_csv("static/data/pokemon.csv")
places = read_objects_from_csv("static/data/places2.csv")
for pokemon in pokemons:
	pokemon["sprite"] = f"static/images/sprites/{pokemon['pokedex_number']}.png"
	pokemon["imgtype1"] = f"static/images/types/{pokemon['type1']}.png"
	pokemon["imgtype2"] = f"static/images/types/{pokemon['type2']}.png"



def get_pokemon_info(csv_file, pokedex_number):
	global pokemons
	print("Recherche du pokemon numéro:", pokedex_number)  # Debug
	for pokemon in pokemons:
		print(f"Comparaison avec {pokemon['pokedex_number']} (type: {type(pokemon['pokedex_number'])}) vs {pokedex_number} (type: {type(pokedex_number)})")  # Debug
		if pokemon['pokedex_number'] == pokedex_number:
			##print("Pokemon trouvé:", pokemon)  # Debug
			return pokemon
	return None

def filter_pokemon(pokemons,input):
	filtered_pokemon=[]
	if input=="":
		return pokemons
	
	for pokemon in pokemons:
		if re.search(input.lower(),pokemon["name"].lower()):
			filtered_pokemon.append(pokemon)
	return filtered_pokemon

def filter_pokemon_type(pokemons,types,input,filterMode="or"):
    if types==[]:
        return filter_pokemon(pokemons,input)
    filtered_pokemon=[]
    for pokemon in pokemons:
        if filterMode=="or" or len(types)==1:
            if re.search(input.lower(),pokemon["name"].lower()):
                if pokemon["type1"] in types or pokemon["type2"] in types:
                    filtered_pokemon.append(pokemon)
        elif filterMode=="and" and len(types)==2:
            if re.search(input.lower(),pokemon["name"].lower()):
                if pokemon["type1"] in types and pokemon["type2"] in types and pokemon["type1"]!=pokemon["type2"]:
                    filtered_pokemon.append(pokemon)
    return filtered_pokemon


# Exemple de graphe simple
def plot_graph():
    fig = go.Figure(data=[go.Scatter(x=[1, 2, 3, 4], y=[2, 4, 6, 8])])
    return fig


### Flask routes


    # Main templates
@app.route('/')
def index():
    return render_template('index.html', pokemons=pokemons)   

@app.route('/pokemon')
def pokemon():
    global places
    
    # info d'un pokemon
    pokedex_number = request.args.get('pokedex_number')
    print("Numéro reçu dans l'URL:", pokedex_number)  # Debug
    pokemon_info = get_pokemon_info("static/data/pokemon.csv", pokedex_number)
    print("Info pokemon retournée:", pokemon_info)  # Debug
    
    # graphe
    fig = plot_graph()
    plot_div = plotly.offline.plot(fig, include_plotlyjs=True, output_type='div')
    
    return render_template('pokemon.html', pokemon_info=pokemon_info, places=places, plot_div=plot_div)


    # Filter

    ##search bar endpoint
@app.route('/search', methods=['POST'])
def search():
    # Récupérer les infos de la requête
    query = request.form.get('query', '')
    types = request.form.getlist('types[]') 
    filterMode=request.form.get('filterMode', '')

    return render_template('search_results.html',pokemons=filter_pokemon_type(pokemons,types,query,filterMode))

    ##type filter endpoint
@app.route('/search_by_type', methods=['POST'])
def search_by_type():
    query = request.form.get('query', '')
    types = request.form.getlist('types[]') 
    filterMode=request.form.get('filterMode', '')
    return render_template('search_results.html', pokemons=filter_pokemon_type(pokemons,types,query,filterMode))

    ##filter mode endpoint
@app.route('/filterMode', methods=['POST'])
def toggle_filter_mode():
    query = request.form.get('query', '')
    types = request.form.getlist('types[]')
    filterMode=request.form.get('filterMode', '')
    return render_template('search_results.html', pokemons=filter_pokemon_type(pokemons,types,query,filterMode))

@app.route('/type/<type_name>')
def type_view(type_name):
    # Filtrer les pokémons par type (type1 ou type2)
    type_pokemons = [p for p in pokemons if p['type1'] == type_name or p['type2'] == type_name]
    
    return render_template('type_view.html', 
                         type_name=type_name,
                         type_pokemons=type_pokemons)




if __name__ == '__main__':
	app.run(debug=True)