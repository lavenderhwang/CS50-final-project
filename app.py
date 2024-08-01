#import SQL
from flask import Flask, flash, redirect, render_template, request, session
import requests
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#setting up databases
app.config['SECRET_KEY'] = 'j8s$3g#7lB8%yWz!2Qk@eN9xCp4+F1uR'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

#Using Spoonacular API
API_KEY = '8e8ffa3209a745789ab98452dd1a8791'
BASE_URL = 'https://api.spoonacular.com/recipes'


@app.route('/')
def home():
    return render_template('layout.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('progress.html')

@app.route('/logout')
def logout():
    return render_template('progress.html')



@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == "POST":
        ingredients = request.form.get('ingredients', '')
        numOfRecipes = request.form.get('numOfRecipes', '')

            # Split the string by commas and strip any extra spaces from each ingredient
        ingredients_list = [ingredient.strip() for ingredient in ingredients.split(',')]

        # Join the list into a comma-separated string with '+,' between ingredients for API request
        ingredients_str = ',+'.join(ingredients_list)

        url = f'{BASE_URL}/findByIngredients?apiKey={API_KEY}&ingredients={ingredients_str}&number={numOfRecipes}&ignorePantry=true'

        response = requests.get(url)
        data = response.json()
        recipes = data

        return render_template('recipes.html', recipes=recipes, missing_ingredients=missing_ingredients)
    else: 
        
        return render_template('search.html')
      
                 
@app.route('/saved')
def saved():

    return render_template('progress.html')


@app.route('/cart')
def cart():
    return render_template('progress.html')


if __name__ == '__main__':
    app.run(debug=True)