from flask import Flask, render_template, json, url_for, request, redirect, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, HiddenField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

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
	administrator = db.Column(db.Boolean, default=False)

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
	pokemon1name = db.Column(db.String(30))
	pokemon2name = db.Column(db.String(30))
	pokemon3name = db.Column(db.String(30))
	pokemon4name = db.Column(db.String(30))
	pokemon5name = db.Column(db.String(30))
	pokemon6name = db.Column(db.String(30))

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(140))
	author = db.Column(db.String(15))
	timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
	teamName = db.Column(db.String(30))

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

class RegisterAdminForm(FlaskForm):
	username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
	email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
	administrator = BooleanField('Is Administrator?')

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
	name = StringField('Team Name', validators=[InputRequired(), Length(min=1, max=50)])
	pokemon1name = HiddenField('Pokemon 1', validators=[InputRequired(), Length(min=1, max=30)])
	pokemon2name = HiddenField('Pokemon 2', validators=[InputRequired(), Length(min=1, max=30)])
	pokemon3name = HiddenField('Pokemon 3', validators=[InputRequired(), Length(min=1, max=30)])
	pokemon4name = HiddenField('Pokemon 4', validators=[InputRequired(), Length(min=1, max=30)])
	pokemon5name = HiddenField('Pokemon 5', validators=[InputRequired(), Length(min=1, max=30)])
	pokemon6name = HiddenField('Pokemon 6', validators=[InputRequired(), Length(min=1, max=30)])

class CommentForm(FlaskForm):
	text = StringField('Text', validators=[InputRequired(), Length(min=1, max=140)])

#with open('static/data/pokemon.json') as pokemon_json:
#	pokemon = json.load(pokemon_json)

pokemon = db.session.query(Pokemon).all()
 
@app.route('/')
def root():
	return redirect(url_for('home'))

@app.route('/home/', methods=['GET', 'POST'])
#@login_required
def home():
	form = TeamForm()
	
	if form.validate_on_submit():
		if current_user.is_authenticated:
			newTeam = Team(name=form.name.data, author=current_user.username, pokemon1name=form.pokemon1name.data, pokemon2name=form.pokemon2name.data, pokemon3name=form.pokemon3name.data, pokemon4name=form.pokemon4name.data, pokemon5name=form.pokemon5name.data, pokemon6name=form.pokemon6name.data)
			db.session.add(newTeam)
			db.session.commit()
	
			url = 'http://set09103.napier.ac.uk:9112/teams/' + form.name.data + '/'	
			return redirect(url)
		else:
			return redirect(url_for('login'))

	return render_template('home.html', pokemon=pokemon, form=form), 200

@app.route('/users/<user_name>/')
@login_required
def userTeams(user_name):
	teams = db.session.query(Team).all()
	teamNames = []

	if user_name == current_user.username:
		for team in teams:
			if user_name == team.author:
				teamNames.append(team.name)

		return render_template('user_teams.html', teamNames=teamNames, name=current_user.username)
	else:
		return render_template('unauthorised_user.html')

@app.route('/teams/')
def teamsList():
	teams = db.session.query(Team).all()
	return render_template('teams.html', teams=teams), 200

		
@app.route('/teams/<team_name>/', methods=['GET', 'POST'])
def teamDetails(team_name):
	form = CommentForm()
	comments = db.session.query(Comment).all()
	teams = db.session.query(Team).all()
	teamNames = []
	
	for team in teams:
		teamNames.append(team.name)

	if team_name in teamNames:
		if form.validate_on_submit():
			if current_user.is_authenticated:
				newComment = Comment(text=form.text.data, author=current_user.username, teamName=team_name)
				db.session.add(newComment)
				db.session.commit()
		
				url = 'http://set09103.napier.ac.uk:9112/teams/' + team_name + '/' 	
				return redirect(url)
			else:
				return redirect(url_for('login'))

		return render_template('team_details.html', pokemon=pokemon, teams=teams, team_name=team_name, comments=comments, form=form)

	else:
		abort(404)

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

		return render_template('invalid.html')

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
		
		return redirect(url_for('login'))
	
	return render_template('register.html', form=form)

@app.route('/admin/register/', methods=['GET', 'POST'], endpoint='adminregister')
def registerAdmin():
	form = RegisterAdminForm()

	if current_user.administrator == True:
		if form.validate_on_submit():
			hashed_password = generate_password_hash(form.password.data, method='sha256')
			newUser = User(username=form.username.data, email=form.email.data, password=hashed_password, administrator=form.administrator.data)
			db.session.add(newUser)
			db.session.commit()

			return render_template('new_admin.html')

		return render_template('register_admin.html', form=form)
	
	else:
		return render_template('admins_only.html')

@app.route('/admin/upload/', methods=['GET', 'POST'], endpoint='adminupload')
def admin():
	form = PokemonForm()
	
	if current_user.administrator == True:
		if form.validate_on_submit():
			newPokemon = Pokemon(id=form.id.data, name=form.name.data, type1=form.type1.data, type2=form.type2.data, evolution=form.evolution.data, ability=form.ability.data, hiddenAbility=form.hiddenAbility.data, pokedexEntry=form.pokedexEntry.data)
		
			db.session.add(newPokemon)
			db.session.commit()
			
			url='http://set09103.napier.ac.uk:9112/pokedex/' + form.name.data + '/'

			return redirect(url)

		return render_template('upload.html', form=form)

	else:
		return render_template('admins_only.html')

pokemonImgDivId1 = None
pokemonImgDivId2 = None
pokemonButtonLabel = None

@app.route('/background_process_2/')
def background_process_2():
	try:
		pokemonButtonId = request.args.get('pokemonButtonId', 0, type=str)

		pokemonImgDivId1 = '#' + pokemonButtonId + 'Div'
		pokemonImgDivId2 = 'img#' + pokemonButtonId + 'Div > img'
		pokemonButtonLabel = '#' + pokemonButtonId + 'Label'
		teamFormHiddenId = '#' + pokemonButtonId + 'name'
		
		return jsonify(pokemonImgDivId2=pokemonImgDivId2, pokemonImgDivId1=pokemonImgDivId1, pokemonButtonLabel=pokemonButtonLabel, teamFormHiddenId=teamFormHiddenId)

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
			return jsonify(result=pokemonName, pokemonImagePath=pokemonImagePath, pokemonImgDivId1=pokemonImgDivId1, pokemonImgDivId2=pokemonImgDivId2, pokemonButtonLabel=pokemonButtonLabel)
		else:
			return jsonify(result=pokemonName + ' does not exist.')

	except Exception as e:
		return str(e)

@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404

if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)
