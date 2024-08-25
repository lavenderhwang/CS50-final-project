#import SQL
from flask import Flask, flash, json, redirect, render_template, request, session
import requests
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from json.decoder import JSONDecodeError
import ast
from nltk.stem import PorterStemmer


from functions import login_required

app = Flask(__name__)

#Using Spoonacular API
API_KEY = '8e8ffa3209a745789ab98452dd1a8791'
BASE_URL = 'https://api.spoonacular.com/recipes'

app.config['SECRET_KEY'] = 'j8s$3g#7lB8%yWz!2Qk@eN9xCp4+F1uR'

#setting up databases
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Setting up basic schema 
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT UNIQUE NOT NULL)
                """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS saved (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_name TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
                )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_name TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
                )""")
    conn.commit()
    cursor.close()
    conn.close()

# Database utility functions

def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

@app.route('/')
def index():
    """Auto Load"""
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers new users"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check for nonempty input
        if not username or not password:
            return "Username and password required", 400
        
        if confirmation != password:
            return "Passwords must match", 400
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure username does not already exist
        try:
            cursor.execute("""INSERT INTO users(username, password) VALUES (?, ?)""", (username, hashed_password ))
            conn.commit()
        except sqlite3.DatabaseError:
            return "username already exists", 400
        finally: 
            cursor.close()
            conn.close()

        return redirect("/login")

    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    """Logs in existing users"""

    #Forgets user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        #check for nonempty input
        if not username or not password:
            return "Username and password required", 400
        
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        #query database for username
        user = cursor.execute("""SELECT * FROM users WHERE username = ?""", (username, )).fetchone()
        
        cursor.close()
        conn.close()

        # Ensure username exists and password is correct
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect("/")
        else:
            return "Invalid username or password", 400

    return render_template("login.html")


@app.route('/logout')
def logout():
    """Logs out existing users"""
    session.clear()

    return redirect("/")


@app.route('/search', methods=['GET','POST'])
@login_required
def search():
    """Search for recipes based on ingredients"""
    if request.method == "POST":
        ingredients = request.form.get('ingredients', '')
        numOfRecipes = request.form.get('numOfRecipes', '')

            # Split the string by commas and strip any extra spaces from each ingredient
        ingredients_list = [ingredient.strip() for ingredient in ingredients.split(',')]

        # Join the list into a comma-separated string with '+,' between ingredients for API request
        ingredients_str = ',+'.join(ingredients_list)

        url = f'{BASE_URL}/findByIngredients?apiKey={API_KEY}&ingredients={ingredients_str}&number={numOfRecipes}&ignorePantry=true'

        response = requests.get(url)
        recipes = response.json()

        

        # Get ingredient count for each recipe
        for recipe in recipes:
            recipe_id = recipe['id']
            recipe_url = f'{BASE_URL}/{recipe_id}/information?apiKey={API_KEY}'
            recipe_info = requests.get(recipe_url)
            recipe_data = recipe_info.json()
            # Add ingredient count
            recipe['ingredient_count'] = len(recipe_data.get('extendedIngredients', []))

            # Extract missing ingredients
            missed_ingredients = recipe.get('missedIngredients', [])
            recipe['missing_ingredients'] = [ingredient['name'] for ingredient in missed_ingredients]
                   
        return render_template('recipes.html', recipes=recipes, recipe_data = recipe_data)
    else: 
        
        return render_template('search.html')

def save_recipe_to_db(user_id, recipe_name, recipe_id, recipe_url, image_url, missing_ingredients):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for existing recipe ID
    cursor.execute("SELECT 1 FROM saved WHERE user_id = ? AND recipe_id = ?", (user_id, recipe_id))
    exists = cursor.fetchone()

    if exists:
        pass
    else:
        cursor.execute("""INSERT INTO saved (user_id, recipe_name, recipe_id, recipe_url, image_url, missing_ingredients) VALUES (?, ?, ?, ?, ?, ?)""", (user_id, recipe_name, recipe_id,recipe_url, image_url, missing_ingredients ))
        conn.commit()
    conn.close()
    
@app.route('/save_recipe', methods=["POST"])
@login_required
def save_recipe():
    user_id = session["user_id"]
    recipe_name = request.form.get('recipe_name')
    recipe_id = request.form.get('recipe_id')
    recipe_url = request.form.get('recipe_url')
    image_url = request.form.get('image_url')
    missing_ingredients = request.form.get('missing_ingredients', '')

    try:
        save_recipe_to_db(user_id, recipe_name, recipe_id, recipe_url, image_url, missing_ingredients)
        return '', 204  # You can also return JSON if needed
    except Exception as e:
        return "Error saving recipe", 500
                 
@app.route('/saved')
@login_required
def saved():
    """Access saved recipes"""
    user_id = session.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM saved WHERE user_id = ?""", (user_id, ))
    recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('saved.html', recipes=recipes)


def add_to_cart_db(user_id, recipe_name, recipe_id, missing_ingredients):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for existing recipe ID
    cursor.execute("SELECT 1 FROM cart WHERE user_id = ? AND recipe_id = ?", (user_id, recipe_id))
    exists = cursor.fetchone()

    if exists:
        pass
    else:
        cursor.execute("""INSERT INTO cart (user_id, recipe_name, recipe_id, missing_ingredients) VALUES (?, ?, ?, ?)""", (user_id, recipe_name, recipe_id, missing_ingredients ))
        conn.commit()
    conn.close()


@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    """Adds recipes to a cart to generate a grocery list of missing ingredients"""
    user_id = session["user_id"]
    recipe_name = request.form.get('recipe_name')
    recipe_id = request.form.get('recipe_id')
    missing_ingredients = request.form.get('missing_ingredients', '')

    try:
        add_to_cart_db(user_id, recipe_name, recipe_id, missing_ingredients)
        return '', 204  # You can also return JSON if needed
    except Exception as e:
        return "Error adding to cart", 500




@app.route('/cart')
@login_required
def cart():
    """Shows recipes in carts and grocery list """
    user_id = session.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT missing_ingredients FROM cart WHERE user_id = ?""", (user_id, ))
    cart_items = cursor.fetchall()
    cursor.execute("""SELECT recipe_name FROM cart WHERE user_id = ?""", (user_id, ))
    recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    # Aggregate and deduplicate ingredients
    all_ingredients = []
    for item in cart_items:
        ingredients_str = item[0]
        ingredients_list = ast.literal_eval(ingredients_str)
        for ingredient in ingredients_list:
            all_ingredients.append(ingredient)

    grocery_list = list(set(all_ingredients))
    alpha_list = sorted(grocery_list)

    recipes = [recipe[0] for recipe in recipes]

    return render_template('cart.html', grocery_list = alpha_list, recipes=recipes)

if __name__ == '__main__':
    init_db()
    app.run(port=8000, debug=True)

  