from flask import Flask, render_template, request, jsonify
import json
import random
import os
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google AI
GOOGLE_API_KEY = 'AIzaSyDi9dguUXe03mjj1eayIFMALyJpIq_Fb4A'
genai.configure(api_key="AIzaSyDi9dguUXe03mjj1eayIFMALyJpIq_Fb4A")

app = Flask(__name__, static_folder='static', template_folder='templates')

# In-memory database for user preferences and recipes
# In a production environment, this would be a proper database
users = {}
recipe_database = {
    "breakfast": [
        {
            "id": "b1",
            "name": "Avocado Toast with Egg",
            "cuisine": "American",
            "calories": 350,
            "protein": 15,
            "carbs": 30,
            "fat": 20,
            "ingredients": [
                {"name": "whole grain bread", "amount": "2 slices"},
                {"name": "avocado", "amount": "1"},
                {"name": "eggs", "amount": "2"},
                {"name": "salt", "amount": "to taste"},
                {"name": "pepper", "amount": "to taste"},
                {"name": "red pepper flakes", "amount": "a pinch"}
            ],
            "instructions": "Toast bread. Mash avocado and spread on toast. Fry eggs and place on top. Season with salt, pepper, and red pepper flakes.",
            "dietary_tags": ["vegetarian"],
            "allergens": ["eggs", "gluten"]
        },
        {
            "id": "b2",
            "name": "Greek Yogurt with Berries and Honey",
            "cuisine": "Mediterranean",
            "calories": 250,
            "protein": 20,
            "carbs": 25,
            "fat": 10,
            "ingredients": [
                {"name": "Greek yogurt", "amount": "1 cup"},
                {"name": "mixed berries", "amount": "1/2 cup"},
                {"name": "honey", "amount": "1 tablespoon"},
                {"name": "granola", "amount": "2 tablespoons"}
            ],
            "instructions": "Add yogurt to a bowl. Top with berries, honey, and granola.",
            "dietary_tags": ["vegetarian"],
            "allergens": ["dairy"]
        },
        {
            "id": "b3",
            "name": "Vegan Smoothie Bowl",
            "cuisine": "American",
            "calories": 300,
            "protein": 10,
            "carbs": 45,
            "fat": 8,
            "ingredients": [
                {"name": "frozen banana", "amount": "1"},
                {"name": "frozen berries", "amount": "1 cup"},
                {"name": "plant-based milk", "amount": "1/2 cup"},
                {"name": "chia seeds", "amount": "1 tablespoon"},
                {"name": "sliced fruits", "amount": "for topping"},
                {"name": "granola", "amount": "2 tablespoons"}
            ],
            "instructions": "Blend banana, berries, and milk until smooth. Pour into a bowl. Top with chia seeds, fruits, and granola.",
            "dietary_tags": ["vegan", "dairy-free"],
            "allergens": []
        }
    ],
    "lunch": [
        {
            "id": "l1",
            "name": "Quinoa Salad with Roasted Vegetables",
            "cuisine": "Mediterranean",
            "calories": 400,
            "protein": 12,
            "carbs": 50,
            "fat": 15,
            "ingredients": [
                {"name": "quinoa", "amount": "1 cup, cooked"},
                {"name": "bell peppers", "amount": "1, diced"},
                {"name": "zucchini", "amount": "1, diced"},
                {"name": "cherry tomatoes", "amount": "1 cup, halved"},
                {"name": "olive oil", "amount": "2 tablespoons"},
                {"name": "lemon juice", "amount": "1 tablespoon"},
                {"name": "feta cheese", "amount": "1/4 cup, crumbled"},
                {"name": "salt and pepper", "amount": "to taste"}
            ],
            "instructions": "Roast vegetables with olive oil, salt, and pepper. Mix with cooked quinoa. Add lemon juice and feta cheese.",
            "dietary_tags": ["vegetarian", "gluten-free"],
            "allergens": ["dairy"]
        },
        {
            "id": "l2",
            "name": "Chicken Wrap with Avocado",
            "cuisine": "American",
            "calories": 450,
            "protein": 30,
            "carbs": 35,
            "fat": 20,
            "ingredients": [
                {"name": "whole wheat wrap", "amount": "1"},
                {"name": "grilled chicken breast", "amount": "4 oz"},
                {"name": "avocado", "amount": "1/2"},
                {"name": "lettuce", "amount": "1 cup, shredded"},
                {"name": "tomato", "amount": "1/2, sliced"},
                {"name": "Greek yogurt", "amount": "2 tablespoons"},
                {"name": "lime juice", "amount": "1 teaspoon"},
                {"name": "salt and pepper", "amount": "to taste"}
            ],
            "instructions": "Mix Greek yogurt with lime juice, salt, and pepper. Spread on wrap. Add chicken, avocado, lettuce, and tomato. Roll up and serve.",
            "dietary_tags": ["high-protein"],
            "allergens": ["gluten", "dairy"]
        },
        {
            "id": "l3",
            "name": "Vegan Buddha Bowl",
            "cuisine": "Asian Fusion",
            "calories": 500,
            "protein": 15,
            "carbs": 70,
            "fat": 18,
            "ingredients": [
                {"name": "brown rice", "amount": "1 cup, cooked"},
                {"name": "chickpeas", "amount": "1/2 cup, roasted"},
                {"name": "sweet potato", "amount": "1, roasted"},
                {"name": "kale", "amount": "2 cups, massaged"},
                {"name": "avocado", "amount": "1/2"},
                {"name": "tahini", "amount": "2 tablespoons"},
                {"name": "lemon juice", "amount": "1 tablespoon"},
                {"name": "maple syrup", "amount": "1 teaspoon"},
                {"name": "salt and pepper", "amount": "to taste"}
            ],
            "instructions": "Arrange rice, chickpeas, sweet potato, and kale in a bowl. Top with avocado. Mix tahini, lemon juice, maple syrup, salt, and pepper for dressing. Drizzle over bowl.",
            "dietary_tags": ["vegan", "gluten-free"],
            "allergens": ["sesame"]
        }
    ],
    "dinner": [
        {
            "id": "d1",
            "name": "Salmon with Roasted Vegetables",
            "cuisine": "American",
            "calories": 500,
            "protein": 35,
            "carbs": 30,
            "fat": 25,
            "ingredients": [
                {"name": "salmon fillet", "amount": "6 oz"},
                {"name": "broccoli", "amount": "1 cup, florets"},
                {"name": "carrots", "amount": "2, sliced"},
                {"name": "olive oil", "amount": "2 tablespoons"},
                {"name": "lemon", "amount": "1/2"},
                {"name": "garlic", "amount": "2 cloves, minced"},
                {"name": "dill", "amount": "1 tablespoon, fresh"},
                {"name": "salt and pepper", "amount": "to taste"}
            ],
            "instructions": "Season salmon with garlic, dill, salt, and pepper. Roast vegetables with olive oil. Bake salmon until flaky. Serve with lemon wedges.",
            "dietary_tags": ["high-protein", "gluten-free"],
            "allergens": ["fish"]
        },
        {
            "id": "d2",
            "name": "Vegetarian Pasta Primavera",
            "cuisine": "Italian",
            "calories": 450,
            "protein": 15,
            "carbs": 65,
            "fat": 15,
            "ingredients": [
                {"name": "whole wheat pasta", "amount": "2 cups, cooked"},
                {"name": "bell peppers", "amount": "1, sliced"},
                {"name": "zucchini", "amount": "1, sliced"},
                {"name": "cherry tomatoes", "amount": "1 cup, halved"},
                {"name": "onion", "amount": "1/2, diced"},
                {"name": "garlic", "amount": "2 cloves, minced"},
                {"name": "olive oil", "amount": "2 tablespoons"},
                {"name": "parmesan cheese", "amount": "1/4 cup, grated"},
                {"name": "basil", "amount": "1/4 cup, fresh"},
                {"name": "salt and pepper", "amount": "to taste"}
            ],
            "instructions": "Sauté vegetables with garlic and olive oil. Toss with pasta. Add parmesan cheese, basil, salt, and pepper.",
            "dietary_tags": ["vegetarian"],
            "allergens": ["gluten", "dairy"]
        },
        {
            "id": "d3",
            "name": "Tofu Stir-Fry with Brown Rice",
            "cuisine": "Asian",
            "calories": 400,
            "protein": 20,
            "carbs": 50,
            "fat": 15,
            "ingredients": [
                {"name": "firm tofu", "amount": "14 oz, cubed"},
                {"name": "brown rice", "amount": "1 cup, cooked"},
                {"name": "broccoli", "amount": "1 cup, florets"},
                {"name": "carrots", "amount": "1, sliced"},
                {"name": "snap peas", "amount": "1 cup"},
                {"name": "soy sauce", "amount": "2 tablespoons"},
                {"name": "sesame oil", "amount": "1 tablespoon"},
                {"name": "ginger", "amount": "1 tablespoon, minced"},
                {"name": "garlic", "amount": "2 cloves, minced"},
                {"name": "sesame seeds", "amount": "1 tablespoon"}
            ],
            "instructions": "Press and cube tofu. Stir-fry with vegetables, ginger, and garlic. Add soy sauce and sesame oil. Serve over brown rice. Garnish with sesame seeds.",
            "dietary_tags": ["vegan", "dairy-free"],
            "allergens": ["soy", "sesame"]
        }
    ],
    "snacks": [
        {
            "id": "s1",
            "name": "Apple with Almond Butter",
            "cuisine": "American",
            "calories": 200,
            "protein": 5,
            "carbs": 25,
            "fat": 10,
            "ingredients": [
                {"name": "apple", "amount": "1"},
                {"name": "almond butter", "amount": "2 tablespoons"}
            ],
            "instructions": "Slice apple. Serve with almond butter for dipping.",
            "dietary_tags": ["vegan", "gluten-free"],
            "allergens": ["nuts"]
        },
        {
            "id": "s2",
            "name": "Greek Yogurt with Honey",
            "cuisine": "Mediterranean",
            "calories": 150,
            "protein": 15,
            "carbs": 15,
            "fat": 5,
            "ingredients": [
                {"name": "Greek yogurt", "amount": "1 cup"},
                {"name": "honey", "amount": "1 tablespoon"}
            ],
            "instructions": "Mix yogurt with honey.",
            "dietary_tags": ["vegetarian", "gluten-free"],
            "allergens": ["dairy"]
        },
        {
            "id": "s3",
            "name": "Hummus with Vegetables",
            "cuisine": "Mediterranean",
            "calories": 150,
            "protein": 5,
            "carbs": 15,
            "fat": 8,
            "ingredients": [
                {"name": "hummus", "amount": "1/4 cup"},
                {"name": "carrots", "amount": "1/2 cup, sliced"},
                {"name": "cucumber", "amount": "1/2 cup, sliced"},
                {"name": "bell pepper", "amount": "1/2 cup, sliced"}
            ],
            "instructions": "Serve hummus with sliced vegetables for dipping.",
            "dietary_tags": ["vegan", "gluten-free"],
            "allergens": ["sesame"]
        }
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/preferences', methods=['POST'])
def save_preferences():
    data = request.json
    user_id = data.get('user_id', str(datetime.now().timestamp()))
    
    # Store user preferences
    users[user_id] = {
        'name': data.get('name', ''),
        'dietary_preferences': data.get('dietary_preferences', []),
        'allergies': data.get('allergies', []),
        'health_goals': data.get('health_goals', ''),
        'cuisines': data.get('cuisines', []),
        'calories_per_day': data.get('calories_per_day', 2000)
    }
    
    return jsonify({'user_id': user_id, 'message': 'Preferences saved successfully'})

@app.route('/api/meal-plan', methods=['POST'])
def generate_meal_plan():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id or user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    user_prefs = users[user_id]
    
    # Generate meal plan based on user preferences
    meal_plan = generate_weekly_meal_plan(user_prefs)
    
    return jsonify({
        'meal_plan': meal_plan,
        'grocery_list': generate_grocery_list(meal_plan)
    })

def filter_recipes_by_preferences(recipes, user_prefs):
    """Filter recipes based on user preferences"""
    filtered = []
    
    for recipe in recipes:
        # Skip if recipe contains allergens
        if any(allergen in recipe['allergens'] for allergen in user_prefs['allergies']):
            continue
            
        # Skip if recipe doesn't match dietary preferences
        if user_prefs['dietary_preferences'] and not any(tag in recipe['dietary_tags'] for tag in user_prefs['dietary_preferences']):
            continue
            
        # Skip if recipe doesn't match cuisine preferences (if specified)
        if user_prefs['cuisines'] and recipe['cuisine'] not in user_prefs['cuisines']:
            continue
            
        filtered.append(recipe)
    
    return filtered

def get_ai_meal_recommendations(user_prefs, meal_type):
    """Get AI-powered meal recommendations based on user preferences"""
    # Create a prompt for the AI model
    prompt = f"""Generate a personalized {meal_type} recipe recommendation for a person with the following preferences:
    - Name: {user_prefs['name']}
    - Dietary preferences: {', '.join(user_prefs['dietary_preferences']) if user_prefs['dietary_preferences'] else 'None'}
    - Allergies: {', '.join(user_prefs['allergies']) if user_prefs['allergies'] else 'None'}
    - Health goals: {user_prefs['health_goals']}
    - Preferred cuisines: {', '.join(user_prefs['cuisines']) if user_prefs['cuisines'] else 'Any'}
    - Daily calorie target: {user_prefs['calories_per_day']} calories
    
    The recipe should include:
    - A creative name
    - Cuisine type
    - Calories, protein, carbs, and fat content
    - List of ingredients with amounts
    - Cooking instructions
    - Dietary tags (e.g., vegetarian, vegan, gluten-free)
    - Potential allergens
    
    Format the response as a JSON object.
    """
    
    try:
        # Generate content using Google's Generative AI
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Extract the text from the response
        recipe_text = response.text.strip()
        
        # Try to parse the JSON response
        try:
            # Clean up the response text to extract JSON
            json_str = recipe_text
            if '```json' in recipe_text:
                json_str = recipe_text.split('```json')[1].split('```')[0].strip()
            elif '```' in recipe_text:
                json_str = recipe_text.split('```')[1].strip()
                
            recipe_json = json.loads(json_str)
            
            # Generate a unique ID for the recipe
            recipe_id = f"{meal_type[0]}{len(recipe_database[meal_type]) + 1}"
            recipe_json['id'] = recipe_id
            
            return recipe_json
        except json.JSONDecodeError as je:
            print(f"JSON parsing error: {je}")
            print(f"Raw response: {recipe_text}")
            return None
    except Exception as e:
        print(f"Error generating AI meal recommendation: {str(e)}")
        return None

def generate_weekly_meal_plan(user_prefs):
    """Generate a weekly meal plan based on user preferences"""
    meal_plan = {}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Filter recipes based on user preferences
    breakfast_options = filter_recipes_by_preferences(recipe_database['breakfast'], user_prefs)
    lunch_options = filter_recipes_by_preferences(recipe_database['lunch'], user_prefs)
    dinner_options = filter_recipes_by_preferences(recipe_database['dinner'], user_prefs)
    snack_options = filter_recipes_by_preferences(recipe_database['snacks'], user_prefs)
    
    # If no recipes match preferences, use default recipes
    if not breakfast_options:
        breakfast_options = recipe_database['breakfast']
    if not lunch_options:
        lunch_options = recipe_database['lunch']
    if not dinner_options:
        dinner_options = recipe_database['dinner']
    if not snack_options:
        snack_options = recipe_database['snacks']
    
    # Generate meal plan for each day
    for day in days:
        daily_calories = 0
        daily_plan = {
            'breakfast': None,
            'lunch': None,
            'dinner': None,
            'snacks': []
        }
        
        # Try to get AI-generated breakfast recipe for some days (e.g., Monday, Wednesday, Friday)
        if day in ['Monday', 'Wednesday', 'Friday']:
            ai_breakfast = get_ai_meal_recommendations(user_prefs, 'breakfast')
            if ai_breakfast:
                daily_plan['breakfast'] = ai_breakfast
                daily_calories += ai_breakfast['calories']
            else:
                breakfast = random.choice(breakfast_options)
                daily_plan['breakfast'] = breakfast
                daily_calories += breakfast['calories']
        else:
            breakfast = random.choice(breakfast_options)
            daily_plan['breakfast'] = breakfast
            daily_calories += breakfast['calories']
        
        # Try to get AI-generated lunch recipe for some days (e.g., Tuesday, Thursday, Saturday)
        if day in ['Tuesday', 'Thursday', 'Saturday']:
            ai_lunch = get_ai_meal_recommendations(user_prefs, 'lunch')
            if ai_lunch:
                daily_plan['lunch'] = ai_lunch
                daily_calories += ai_lunch['calories']
            else:
                lunch = random.choice(lunch_options)
                daily_plan['lunch'] = lunch
                daily_calories += lunch['calories']
        else:
            lunch = random.choice(lunch_options)
            daily_plan['lunch'] = lunch
            daily_calories += lunch['calories']
        
        # Try to get AI-generated dinner recipe for some days (e.g., Sunday)
        if day in ['Sunday']:
            ai_dinner = get_ai_meal_recommendations(user_prefs, 'dinner')
            if ai_dinner:
                daily_plan['dinner'] = ai_dinner
                daily_calories += ai_dinner['calories']
            else:
                dinner = random.choice(dinner_options)
                daily_plan['dinner'] = dinner
                daily_calories += dinner['calories']
        else:
            dinner = random.choice(dinner_options)
            daily_plan['dinner'] = dinner
            daily_calories += dinner['calories']
        
        # Add snacks (up to 2)
        remaining_calories = user_prefs['calories_per_day'] - daily_calories
        snack_count = min(2, remaining_calories // 150)  # Rough estimate
        
        for _ in range(snack_count):
            snack = random.choice(snack_options)
            daily_plan['snacks'].append(snack)
            daily_calories += snack['calories']
        
        meal_plan[day] = daily_plan
    
    return meal_plan

def generate_grocery_list(meal_plan):
    """Generate a grocery list based on the meal plan"""
    grocery_items = {}
    
    # Iterate through each day's meals
    for day, meals in meal_plan.items():
        # Process breakfast
        for ingredient in meals['breakfast']['ingredients']:
            name = ingredient['name']
            amount = ingredient['amount']
            if name in grocery_items:
                grocery_items[name]['days'].append(f"{day} (Breakfast)")
            else:
                grocery_items[name] = {
                    'amount': amount,
                    'days': [f"{day} (Breakfast)"]
                }
        
        # Process lunch
        for ingredient in meals['lunch']['ingredients']:
            name = ingredient['name']
            amount = ingredient['amount']
            if name in grocery_items:
                grocery_items[name]['days'].append(f"{day} (Lunch)")
            else:
                grocery_items[name] = {
                    'amount': amount,
                    'days': [f"{day} (Lunch)"]
                }
        
        # Process dinner
        for ingredient in meals['dinner']['ingredients']:
            name = ingredient['name']
            amount = ingredient['amount']
            if name in grocery_items:
                grocery_items[name]['days'].append(f"{day} (Dinner)")
            else:
                grocery_items[name] = {
                    'amount': amount,
                    'days': [f"{day} (Dinner)"]
                }
        
        # Process snacks
        for snack in meals['snacks']:
            for ingredient in snack['ingredients']:
                name = ingredient['name']
                amount = ingredient['amount']
                if name in grocery_items:
                    grocery_items[name]['days'].append(f"{day} (Snack)")
                else:
                    grocery_items[name] = {
                        'amount': amount,
                        'days': [f"{day} (Snack)"]
                    }
    
    # Convert to list format
    grocery_list = []
    for name, details in grocery_items.items():
        grocery_list.append({
            'name': name,
            'amount': details['amount'],
            'used_in': details['days']
        })
    
    # Sort alphabetically
    grocery_list.sort(key=lambda x: x['name'])
    
    return grocery_list

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Get all recipes"""
    all_recipes = []
    for category in recipe_database:
        all_recipes.extend(recipe_database[category])
    return jsonify(all_recipes)

@app.route('/api/recipe/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get a specific recipe by ID"""
    for category in recipe_database:
        for recipe in recipe_database[category]:
            if recipe['id'] == recipe_id:
                return jsonify(recipe)
    return jsonify({'error': 'Recipe not found'}), 404

@app.route('/api/feedback', methods=['POST'])
def save_feedback():
    """Save user feedback on meal plan"""
    data = request.json
    user_id = data.get('user_id')
    feedback = data.get('feedback', {})
    
    if not user_id or user_id not in users:
        return jsonify({'error': 'User not found'}), 404
    
    # Store feedback for future improvements
    if 'feedback' not in users[user_id]:
        users[user_id]['feedback'] = []
    
    users[user_id]['feedback'].append({
        'date': datetime.now().isoformat(),
        'feedback': feedback
    })
    
    return jsonify({'message': 'Feedback saved successfully'})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        # Configure Gemini
        genai.configure(api_key="AIzaSyDi9dguUXe03mjj1eayIFMALyJpIq_Fb4A")
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Generate response
        response = model.generate_content(message)
        
        if response and hasattr(response, 'text'):
            # Clean up the response text by removing excessive asterisks
            cleaned_response = response.text.replace('**', '')
            return jsonify({
                'response': cleaned_response,
                'success': True
            })
        else:
            return jsonify({
                'response': "I couldn't generate a response. Please try again.",
                'success': False
            })
            
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return jsonify({
            'response': f"An error occurred: {str(e)}",
            'success': False
        }), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    try:
        data = request.json
        text = data.get('text', '')
        
        # Configure Gemini
        genai.configure(api_key="AIzaSyDi9dguUXe03mjj1eayIFMALyJpIq_Fb4A")
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Create prompt for summarization
        prompt = f"Please provide a concise summary of the following text, highlighting only the key points:\n\n{text}"
        
        # Generate summary
        response = model.generate_content(prompt)
        
        if response and hasattr(response, 'text'):
            # Clean up the response text
            summary = response.text.replace('**', '')
            return jsonify({
                'summary': summary,
                'success': True
            })
        else:
            return jsonify({
                'summary': "I couldn't generate a summary. Please try again.",
                'success': False
            })
            
    except Exception as e:
        print(f"Error in summarize: {str(e)}")
        return jsonify({
            'summary': f"An error occurred: {str(e)}",
            'success': False
        }), 500

if __name__ == '__main__':
    app.run(debug=True)