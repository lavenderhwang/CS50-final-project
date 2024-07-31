#import SQL
from flask import Flask, flash, redirect, render_template, request
import requests

app = Flask(__name__)

#Using Spoonacular API
API_KEY = '8e8ffa3209a745789ab98452dd1a8791'
BASE_URL = 'https://api.spoonacular.com/recipes'


@app.route('/')
def home():
    return render_template('layout.html')



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
    
        return render_template('recipes.html', recipes=recipes)
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