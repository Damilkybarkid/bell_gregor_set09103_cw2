from flask import Flask, render_template, json, url_for, request, redirect
app = Flask(__name__)

with open('static/data/pokemon.json') as pokemon_json:
	pokemon = json.load(pokemon_json)

@app.route('/')
def root():
	return redirect(url_for('home'))

@app.route('/home/')
def home():
	return render_template('home.html'), 200

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

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
