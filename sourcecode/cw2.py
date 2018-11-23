from flask import Flask, render_template, json, url_for, request, redirect, jsonify
app = Flask(__name__)

with open('static/data/pokemon.json') as pokemon_json:
	pokemon = json.load(pokemon_json)

@app.route('/')
def root():
	return redirect(url_for('home'))

@app.route('/home/')
def home():
	return render_template('home.html', pokemon=pokemon), 200

@app.route('/pokedex/')
def pokedex():
	return render_template('pokedex.html', pokemon=pokemon), 200

@app.route('/pokedex/<pokemon_name>/')
def pokemonDetails(pokemon_name):
	pokemon_names=[]

	for monster in pokemon:
		pokemon_names.append(monster["name"])
	
	if pokemon_name in pokemon_names:
		return render_template('pokemon_details.html', pokemon=pokemon, pokemon_name=pokemon_name)
	else:
		abort(404)

@app.route('/background_process/')
def background_process():
	try:
		pokemonName = request.args.get('pokemonName', 0, type=str)
		pokemon_names=[]

		for monster in pokemon:
			pokemon_names.append(monster["name"])

		if pokemonName in pokemon_names:
			pokemonImagePath = '/static/images/gifs/' + pokemonName + '.gif'
			return jsonify(result=pokemonName, pokemonImagePath=pokemonImagePath)
		else:
			return jsonify(result=pokemonName + ' does not exist.')

	except Exception as e:
		return str(e)

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
