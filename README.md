# AI Meal Planning Chatbot

A responsive web application that helps users create personalized meal plans based on their dietary preferences, restrictions, and health goals.

## Features

- Interactive chat interface for gathering user preferences
- Personalized weekly meal plan generation
- Detailed recipes with ingredient measurements
- Automated grocery list creation
- Support for multiple cuisines and dietary restrictions
- Feedback system for meal plan improvement
- Mobile-responsive design

## Tech Stack

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript
- **Data Storage**: In-memory database (can be extended to use a proper database)

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository or download the source code

2. Navigate to the project directory

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python Meal-Planner-Chat-Bot-main/app.py    #python app.py
   ```

5. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

## How to Use

1. When you first open the application, the chatbot will greet you and ask for your name.

2. Answer the chatbot's questions about your:
   - Dietary preferences (vegetarian, vegan, etc.)
   - Food allergies or restrictions
   - Health goals
   - Cuisine preferences
   - Daily calorie target

3. The chatbot will generate a personalized weekly meal plan based on your inputs.

4. You can:
   - View meals for each day of the week
   - Click on meals to see detailed recipes
   - Generate a grocery list for the entire week
   - Provide feedback to improve future meal plans
   - Create a new meal plan when needed

## Customization

The application comes with a pre-loaded recipe database in `app.py`. You can extend this database by adding more recipes following the same format.

## Future Enhancements

- User authentication system
- Persistent storage with a database
- More advanced nutritional analysis
- Recipe rating system
- Meal plan export functionality
- Integration with grocery delivery services

## License

MIT License