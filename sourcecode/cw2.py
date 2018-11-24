from flask import Flask, render_template, json, url_for, request, redirect, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Supersecretnevertellno-one'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///var/database.db'
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))

class Pokemon(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)
	type1 = db.Column(db.String(10))
	type2 = db.Column(db.String(10))
	evolution = db.Column(db.String(30))
	ability = db.Column(db.String(30))
	hiddenAbility = db.Column(db.String(30))
	pokedexEntry = db.Column(db.String(1000))

class Team(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=True)
	author = db.Column(db.String(15))
	pokemon1 = db.Column(db.String(30))
	pokemon2 = db.Column(db.String(30))
	pokemon3 = db.Column(db.String(30))
	pokemon4 = db.Column(db.String(30))
	pokemon5 = db.Column(db.String(30))
	pokemon6 = db.Column(db.String(30))

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
	remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
	username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
	email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class PokemonForm(FlaskForm):
	id = IntegerField('ID', validators=[InputRequired()])
	name = StringField('Name', validators=[InputRequired(), Length(min=1, max=30)])
	type1 = StringField('Type 1', validators=[InputRequired(), Length(min=1, max=10)])
	type2 = StringField('Type 2', validators=[InputRequired(), Length(min=1, max=10)])
	evolution = StringField('Evolution', validators=[InputRequired(), Length(min=1, max=30)])
	ability = StringField('Ability', validators=[InputRequired(), Length(min=1, max=30)])
	hiddenAbility = StringField('Hidden Ability', validators=[InputRequired(), Length(min=1, max=30)])
	pokedexEntry = StringField('Pokedex Entry', validators=[InputRequired(), Length(min=1, max=1000)])
	
class TeamForm(FlaskForm):
	name = StringField('Name', validators=[InputRequired(), Length(min=1, max=50)])

#with open('static/data/pokemon.json') as pokemon_json:
#	pokemon = json.load(pokemon_json)

pokemon = db.session.query(Pokemon).all()

@app.route('/')
def root():
	return redirect(url_for('home'))

@app.route('/home/')
#@login_required
def home():
	form = TeamForm()

	return render_template('home.html', pokemon=pokemon, name=current_user.username, form=form), 200

@app.route('/pokedex/')
def pokedex():
	return render_template('pokedex.html', pokemon=pokemon), 200

@app.route('/pokedex/<pokemon_name>/')
def pokemonDetails(pokemon_name):
	pokemonNames = []

	for monster in pokemon:
		pokemonNames.append(monster.name)
	
	if pokemon_name in pokemonNames:
		return render_template('pokemon_details.html', pokemon=pokemon, pokemon_name=pokemon_name)
	else:
		abort(404)

@app.route('/login/', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('home'))		

		return '<h1>Invalid username or password</h1>'
		#return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

	return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
	form = RegisterForm()

	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method='sha256')
		newUser = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(newUser)
		db.session.commit()		
		
		return '<h1>New user has been created!</h1>'
		#return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
	return render_template('register.html', form=form)

@app.route('/admin/', methods=['GET', 'POST'])
def admin():
	form = PokemonForm()

	if form.validate_on_submit():
		newPokemon = Pokemon(id=form.id.data, name=form.name.data, type1=form.type1.data, type2=form.type2.data, evolution=form.evolution.data, ability=form.ability.data, hiddenAbility=form.hiddenAbility.data, pokedexEntry=form.pokedexEntry.data)
		
		db.session.add(newPokemon)
		db.session.commit()

		return '<h1>Pokemon has been added!</h1>'
	return render_template('admin.html', form=form)


pokemonImgDivId1 = None
pokemonImgDivId2 = None

@app.route('/background_process_2/')
def background_process_2():
	try:
		pokemonButtonId = request.args.get('pokemonButtonId', 0, type=str)

		pokemonImgDivId1 = '#' + pokemonButtonId + 'Div'
		pokemonImgDivId2 = 'img#' + pokemonButtonId + 'Div > img'
		
		return jsonify(pokemonImgDivId2=pokemonImgDivId2, pokemonImgDivId1=pokemonImgDivId1)

	except Exception as e:
		return str(e) 

@app.route('/background_process/')
def background_process():
	try:
		pokemonName = request.args.get('pokemonName', 0, type=str)
		pokemonNames=[]
		
			

		for monster in pokemon:
			pokemonNames.append(monster.name)

		if pokemonName in pokemonNames:
			pokemonImagePath = '/static/images/gifs/' + pokemonName + '.gif'
			return jsonify(result=pokemonName, pokemonImagePath=pokemonImagePath, pokemonImgDivId1=pokemonImgDivId1, pokemonImgDivId2=pokemonImgDivId2)
		else:
			return jsonify(result=pokemonName + ' does not exist.')

	except Exception as e:
		return str(e)

		

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
