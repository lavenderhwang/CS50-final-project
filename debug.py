import requests

API_KEY = '8e8ffa3209a745789ab98452dd1a8791'
BASE_URL = 'https://api.spoonacular.com/recipes'

ingredients_list = ['tomato', 'egg', 'peanuts']
ingredients_str = ',+'.join(ingredients_list)


url = f'{BASE_URL}/findByIngredients?apiKey={API_KEY}&ingredients={ingredients_str}&number=1&ignorePantry=true'

response = requests.get(url)
data = response.json()
recipes = data

print(f'Recipes: {recipes}')