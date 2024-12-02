import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import psycopg2

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server 

# Hardcoded PostgreSQL connection string from Render (replace with your own credentials)
DB_URL = "postgresql://xaisurvey_user:LaMSpNwIrn0dezLAxZmJ3w4wtqfO13J4@dpg-ct13btbtq21c73el6r20-a/xaisurvey"  # Replace this with your actual connection string from Render

# Connect to PostgreSQL database
def connect_db():
    try:
        # Use the hardcoded connection string
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Ensure that the survey_results table exists
def create_table_if_not_exists():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_results (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255),
                    age INT,
                    gender VARCHAR(50),
                    feedback TEXT
                )
            """)
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            conn.close()

# Call the function to create the table if it doesn't exist
create_table_if_not_exists()

# Layout of the app
app.layout = html.Div([
    html.H1("Survey Form"),

    # Survey form elements
    dcc.Input(id='name', type='text', placeholder="Enter your name", style={'margin': '10px'}),
    dcc.Input(id='age', type='number', placeholder="Enter your age", style={'margin': '10px'}),
    dcc.Dropdown(
        id='gender',
        options=[
            {'label': 'Male', 'value': 'Male'},
            {'label': 'Female', 'value': 'Female'},
            {'label': 'Other', 'value': 'Other'}
        ],
        placeholder="Select gender",
        style={'margin': '10px'}
    ),
    dcc.Textarea(
        id='feedback',
        placeholder="Enter your feedback here",
        style={'width': '100%', 'height': '150px', 'margin': '10px'}
    ),
    html.Button('Submit', id='submit-button', n_clicks=0, style={'margin': '10px'}),
    html.Div(id='response-message', style={'margin': '10px'})
])


# Callback to handle the form submission
@app.callback(
    Output('response-message', 'children'),
    [Input('submit-button', 'n_clicks')],
    [dash.dependencies.State('name', 'value'),
     dash.dependencies.State('age', 'value'),
     dash.dependencies.State('gender', 'value'),
     dash.dependencies.State('feedback', 'value')]
)
def submit_form(n_clicks, name, age, gender, feedback):
    if n_clicks > 0:
        # Validate input data
        if not name or not age or not gender or not feedback:
            return "Please fill in all fields."

        # Insert the survey data into PostgreSQL
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO survey_results (name, age, gender, feedback)
                    VALUES (%s, %s, %s, %s)
                """, (name, age, gender, feedback))
                conn.commit()
                cursor.close()
                return f"Thank you for your submission, {name}!"
            except Exception as e:
                return f"Error saving data: {e}"
            finally:
                conn.close()
        else:
            return "Error connecting to the database."


# Make sure Gunicorn uses Flask server (expose the server object)
if __name__ == '__main__':
    app.run_server(debug=True)
