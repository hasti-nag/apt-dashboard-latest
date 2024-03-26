import os

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, State
from dash.dependencies import Input, Output
from flask import Flask, request, session, redirect, url_for, render_template, send_from_directory
from dash import html

from plotly.subplots import make_subplots

from database import get_database_connection

app = Flask(__name__)
app.secret_key = '3195162'  # Change this to a secure secret key
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/', suppress_callback_exceptions=True,
                     external_stylesheets=[dbc.themes.SOLAR])
dash_app1 = dash.Dash(__name__, server=app, url_base_pathname='/polling_data_analysis/',
                      suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.SOLAR])

# Define the path to the logo image
logo_path = os.path.join('static', 'logo.jpeg')


@app.route('/static/<filename>')
def serve_image(filename):
    return send_from_directory('templates/static', filename)


@app.route("/")
def login():
    return render_template("login.html")


# Authentication route
@app.route('/authenticate', methods=['POST'])
def authenticate():
    # Add your authentication logic here (e.g., check username and password)
    username = request.form['username']
    password = request.form['password']

    conn = get_database_connection()
    cursor = conn.cursor()
    # Fetch user from the database based on the entered username
    query = """SELECT * FROM dashboard_login WHERE username = %s;"""
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    # Check if the user exists and the password is correct
    if user and user[2] == password:  # Assuming the password is in the third column
        session['logged_in'] = True
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


# Dashboard route
@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'logged_in' in session and session['logged_in']:
        return dash_app.index()
    else:
        return redirect(url_for('login'))


# Polling Data Dashboard route
@app.route('/polling_data_analysis')
def polling_data_analysis():
    # Check if the user is logged in
    if 'logged_in' in session and session['logged_in']:
        return dash_app1.index()
    else:
        return redirect(url_for('login'))


# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Update the styling for dropdown components
dropdown_style = {'width': '80%'}
# Define the layout of the dashboard
dash_app.layout = html.Div(style={'backgroundColor': '#f2f2f2'}, children=[
    dcc.Location(id='dash-url', refresh=False),
    html.Div(id='total-voters', style={'display': 'none'}),
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Voter Statistics Dashboard", className="mb-2", style={'color': 'blue'})),
            dbc.Col(html.Div(id='welcome-message', children=[], style={'text-align': 'right', 'font-size': '18px'}))
        ]),
        dbc.Row([
            dbc.Col([], width={"size": 6, "order": "first"}),  # Empty column to push elements to the right
            dbc.Col(html.A("Polling Data Analysis", href="/polling_data_analysis", style={'color': 'red'}),
                    width={"size": 2, "order": "last", "offset": 0}, lg=2, md=3, sm=4, xs=12),
            dbc.Col(html.A("Logout", href="/logout", style={'color': 'orange'}),
                    width={"size": 2, "order": "last", "offset": 0}, lg=2, md=3, sm=4, xs=12),
            dbc.Col(html.Button('Reset', id='reset-button', n_clicks=0, style={'color': 'blue'}),
                    width={"size": 2, "order": "last", "offset": 0}, lg=2, md=3, sm=4, xs=12),
            html.Button('Print as a PDF', id='download-pdf-button', className='btn btn-link text-primary',
                        style={'textDecoration': 'none'}),
            html.Div(id='dummy-output', style={'display': 'none'})
        ]),
        dbc.Row([
            dbc.Col([
                html.Label("Caste:", className="required-field"),
                html.Div("*", style={'color': 'red', 'display': 'inline-block', 'marginLeft': '5px'}),
                dcc.Dropdown(
                    id='caste-dropdown',
                    options=[],
                    multi=False,
                    value=None,
                    placeholder="Select Caste",
                    style=dropdown_style,
                ),
            ]),
            dbc.Col([
                html.Label("Sub-Caste:"),
                dcc.Dropdown(
                    id='sub-caste-dropdown',
                    options=[],
                    multi=False,
                    value=None,
                    placeholder="Select Sub-Caste",
                    style=dropdown_style,
                ),
            ]),
            dbc.Col([
                html.Label("District:"),
                dcc.Dropdown(
                    id='district-dropdown',
                    options=[],
                    multi=False,
                    value=None,
                    placeholder="Select District",
                    style=dropdown_style,
                ),
            ]),
            dbc.Col([
                html.Label("Parliamentary Constituency:"),
                dcc.Dropdown(
                    id='parliamentary-constituency-dropdown',
                    options=[],
                    multi=False,
                    value=None,
                    placeholder="Select Parliamentary Constituency",
                    style=dropdown_style,
                ),
            ]),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                html.Label("Assembly Constituency:"),
                dcc.Dropdown(
                    id='assembly-constituency-dropdown',
                    options=[],
                    multi=False,
                    value=None,
                    placeholder="Select Assembly Constituency",
                    style=dropdown_style,
                ),
            ]),
            dbc.Col([
                html.Label("Mandal:"),
                dcc.Dropdown(
                    id='mandal-dropdown',
                    options=[],
                    multi=False,
                    value=None,
                    placeholder="Select Mandal",
                    style=dropdown_style,
                ),
            ]),
            dbc.Col([
                html.Label("Village:"),
                dcc.Dropdown(
                    id='village-dropdown',
                    options=[],
                    multi=False,
                    value=None,
                    placeholder="Select Village",
                    style=dropdown_style,
                ),
            ]),
            dbc.Col([
                html.Label("Booth:"),
                dcc.Dropdown(
                    id='booth-dropdown',
                    options=[],
                    multi=False,
                    value=None,
                    placeholder="Select Booth",
                    style=dropdown_style,
                ),
            ]),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                html.H2("Voter Caste Breakdown", className="text-center"),  # Title for the pie chart
                dcc.Graph(id='voter-pie-chart', className="mt-4", style={'height': '600px'}),
            ], width={"size": 12, "order": "first", "offset": 0}, lg=4, md=12, sm=12, xs=12),
            dbc.Col([
                html.H2("Voter Sub-Caste Breakdown", className="text-center"),  # Title for the sub-caste breakdown
                dcc.Graph(id='voter-sub-caste-chart', className="mt-4", style={'height': '600px'}),
            ], width={"size": 12, "order": "last", "offset": 0}, lg=8, md=12, sm=12, xs=12),
        ], className="mb-4"),
    ], fluid=True)
])

# JavaScript to trigger print when the button is clicked
dash_app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            var buttonsToHide = document.querySelectorAll('.btn, #reset-button');
            buttonsToHide.forEach(function(button) {
                button.style.display = 'none';
            });
            // Hide labels and dropdowns
            var labelsAndDropdowns = document.querySelectorAll('label, select');
            console.log(labelsAndDropdowns); // Check if the elements are correctly selected
            labelsAndDropdowns.forEach(function(element) {
                element.style.display = 'none';
            });

            // Hide the print as PDF row
            var welcomeMessage = document.querySelector('#welcome-message');
            if (welcomeMessage) {
                welcomeMessage.style.display = 'none';
            }
            // Hide Dashboard and Logout links
            var pollingLink = document.querySelector('a[href="/polling_data_analysis"]');
            if (pollingLink) {
                pollingLink.style.display = 'none';
            }
            var logoutLink = document.querySelector('a[href="/logout"]');
            if (logoutLink) {
                logoutLink.style.display = 'none';
            }
            var printButtonRow = document.querySelector('#caste-dropdown');
            if (printButtonRow) {
                printButtonRow.style.display = 'none';
            }
            var printButtonRow1 = document.querySelector('#sub-caste-dropdown');
            if (printButtonRow1) {
                printButtonRow1.style.display = 'none';
            }
            var printButtonRow2 = document.querySelector('#district-dropdown');
            if (printButtonRow2) {
                printButtonRow2.style.display = 'none';
            }
            var printButtonRow3 = document.querySelector('#parliamentary-constituency-dropdown');
            if (printButtonRow3) {
                printButtonRow3.style.display = 'none';
            }
            var printButtonRow4 = document.querySelector('#assembly-constituency-dropdown');
            if (printButtonRow4) {
                printButtonRow4.style.display = 'none';
            }
            var printButtonRow5 = document.querySelector('#mandal-dropdown');
            if (printButtonRow5) {
                printButtonRow5.style.display = 'none';
            }
            var printButtonRow6 = document.querySelector('#village-dropdown');
            if (printButtonRow6) {
                printButtonRow6.style.display = 'none';
            }
            var printButtonRow7 = document.querySelector('#booth-dropdown');
            if (printButtonRow7) {
                printButtonRow7.style.display = 'none';
            }
            // Print the window
            window.print();

            // Show labels, dropdowns, and the print as PDF row again after printing
            labelsAndDropdowns.forEach(function(element) {
                element.style.display = '';
            });
            buttonsToHide.forEach(function(button) {
                button.style.display = '';
            });
            if (printButtonRow) {
                printButtonRow.style.display = '';
            }
            if (printButtonRow1) {
                printButtonRow1.style.display = '';
            }
            if (printButtonRow2) {
                printButtonRow2.style.display = '';
            }
            if (printButtonRow3) {
                printButtonRow3.style.display = '';
            }
            if (printButtonRow4) {
                printButtonRow4.style.display = '';
            }
            if (printButtonRow5) {
                printButtonRow5.style.display = '';
            }
            if (printButtonRow6) {
                printButtonRow6.style.display = '';
            }
            if (printButtonRow7) {
                printButtonRow7.style.display = '';
            }
            if (welcomeMessage) {
                welcomeMessage.style.display = '';
            }
            if (pollingLink) {
                pollingLink.style.display = '';
            }
            if (logoutLink) {
                logoutLink.style.display = '';
            }
        }
    }
    """,
    Output('dummy-output', 'children'),
    [Input('download-pdf-button', 'n_clicks')]
)


# Callback to update the welcome message
@dash_app.callback(
    Output('welcome-message', 'children'),
    [Input('dash-url', 'pathname')]
)
def update_welcome_message(pathname):
    if 'logged_in' in session and session['logged_in']:
        return html.Div([
            html.H3(f"Welcome, {session['username']}! | "),
        ])
    return ''


# Callback to update options for caste dropdown
@dash_app.callback(
    Output('caste-dropdown', 'options'),
    [Input('caste-dropdown', 'value')]
)
def update_caste_options(selected_caste):
    conn = get_database_connection()
    cursor = conn.cursor()

    # Fetch all distinct castes from the database
    query = """SELECT DISTINCT caste_id, caste FROM BLI WHERE caste NOT IN ('Dead', 'Deleted', 'Not Traced') ORDER BY caste;"""
    cursor.execute(query)
    caste_options = [{'label': caste, 'value': caste_id} for caste_id, caste in cursor.fetchall()]

    cursor.close()
    conn.close()

    return caste_options


# Callback to update options for district dropdown
@dash_app.callback(
    Output('district-dropdown', 'options'),
    [Input('caste-dropdown', 'value')]
)
def update_district_options(selected_district):
    conn = get_database_connection()
    cursor = conn.cursor()

    # Fetch all distinct districts from the database
    query = """SELECT DISTINCT district_code, district_name FROM BLI ORDER BY district_name;"""
    cursor.execute(query)
    district_options = [{'label': district, 'value': district_code} for district_code, district in cursor.fetchall()]

    district_options.insert(0, {'label': 'All', 'value': 'districtall'})

    cursor.close()
    conn.close()

    return district_options


# Callback to update options for PC dropdown
@dash_app.callback(
    Output('parliamentary-constituency-dropdown', 'options'),
    [Input('district-dropdown', 'value')]
)
def update_pc_options(selected_district):
    conn = get_database_connection()
    cursor = conn.cursor()
    if selected_district and selected_district != 'districtall':
        # Fetch all distinct pcs from the database
        query = """SELECT DISTINCT pc_code, pc_name FROM BLI WHERE district_code = %s ORDER BY pc_name;"""

        cursor.execute(query, (selected_district,))
        pc_options = [{'label': pc_name, 'value': pc_code} for pc_code, pc_name in cursor.fetchall()]

        pc_options.insert(0, {'label': 'All', 'value': 'pcall'})

        cursor.close()
        conn.close()
    else:
        # Fetch all distinct pcs from the database
        query = """SELECT DISTINCT pc_code, pc_name FROM BLI ORDER BY pc_name;"""

        cursor.execute(query)
        pc_options = [{'label': pc_name, 'value': pc_code} for pc_code, pc_name in cursor.fetchall()]

        pc_options.insert(0, {'label': 'All', 'value': 'pcall'})

        cursor.close()
        conn.close()

    return pc_options


# Callback to update options for AC dropdown
@dash_app.callback(
    Output('assembly-constituency-dropdown', 'options'),
    [Input('district-dropdown', 'value'),
     Input('parliamentary-constituency-dropdown', 'value')]
)
def update_ac_options(selected_district, selected_pc):
    conn = get_database_connection()
    cursor = conn.cursor()
    if selected_district and selected_district != 'districtall' and selected_pc and selected_pc != 'pcall':
        # Fetch all distinct acs from the database
        query = """SELECT DISTINCT ac_no, ac_name FROM BLI WHERE district_code = %s AND pc_code = %s ORDER BY ac_name;"""

        cursor.execute(query, (selected_district, selected_pc))
        ac_options = [{'label': ac_name, 'value': ac_no} for ac_no, ac_name in cursor.fetchall()]

        ac_options.insert(0, {'label': 'All', 'value': 'acall'})
        cursor.close()
        conn.close()
    else:
        # Fetch all distinct acs from the database
        query = """SELECT DISTINCT ac_no, ac_name FROM BLI ORDER BY ac_name;"""

        cursor.execute(query)
        ac_options = [{'label': ac_name, 'value': ac_no} for ac_no, ac_name in cursor.fetchall()]

        ac_options.insert(0, {'label': 'All', 'value': 'acall'})
        cursor.close()
        conn.close()

    return ac_options


# Callback to update options for Mandal dropdown
@dash_app.callback(
    Output('mandal-dropdown', 'options'),
    [Input('district-dropdown', 'value'),
     Input('parliamentary-constituency-dropdown', 'value'),
     Input('assembly-constituency-dropdown', 'value')]
)
def update_mandal_options(selected_district, selected_pc, selected_ac):
    conn = get_database_connection()
    cursor = conn.cursor()
    if selected_district and selected_district != 'districtall' and selected_pc and selected_pc != 'pcall' and selected_ac != 'acall':
        # Fetch all distinct acs from the database
        query = """SELECT DISTINCT mandal_id, mandal_name FROM BLI WHERE district_code = %s AND pc_code = %s AND ac_no = %s ORDER BY mandal_name;"""

        cursor.execute(query, (selected_district, selected_pc, selected_ac))
        mandal_options = [{'label': mandal_name, 'value': mandal_id} for mandal_id, mandal_name in cursor.fetchall()]

        cursor.close()
        conn.close()
    elif selected_ac != 'acall':
        # Fetch all distinct acs from the database
        query = """SELECT DISTINCT mandal_id, mandal_name FROM BLI WHERE ac_no = %s ORDER BY mandal_name;"""

        cursor.execute(query, (selected_ac, ))
        mandal_options = [{'label': mandal_name, 'value': mandal_id} for mandal_id, mandal_name in cursor.fetchall()]

        cursor.close()
        conn.close()
    else:
        mandal_options = []

    return mandal_options


# Callback to update options for village dropdown
@dash_app.callback(
    Output('village-dropdown', 'options'),
    [Input('district-dropdown', 'value'),
     Input('parliamentary-constituency-dropdown', 'value'),
     Input('assembly-constituency-dropdown', 'value'),
     Input('mandal-dropdown', 'value')]
)
def update_village_options(selected_district, selected_pc, selected_ac, selected_mandal):
    conn = get_database_connection()
    cursor = conn.cursor()
    if selected_district and selected_district != 'districtall' and selected_pc and selected_pc != 'pcall' and selected_ac != 'acall' and selected_ac and selected_mandal:
        # Fetch all distinct villages from the database
        query = """SELECT DISTINCT village_id, village_name FROM BLI WHERE district_code = %s AND pc_code = %s and ac_no = %s AND mandal_id = %s ORDER BY village_name;"""

        cursor.execute(query, (selected_district, selected_pc, selected_ac, selected_mandal))
        village_options = [{'label': village_name, 'value': village_id} for village_id, village_name in cursor.fetchall()]

        cursor.close()
        conn.close()
    elif selected_ac != 'acall' and selected_mandal:
        # Fetch all distinct villages from the database
        query = """SELECT DISTINCT village_id, village_name FROM BLI WHERE ac_no = %s AND mandal_id = %s ORDER BY village_name;"""

        cursor.execute(query, (selected_ac, selected_mandal))
        village_options = [{'label': village_name, 'value': village_id} for village_id, village_name in cursor.fetchall()]

        cursor.close()
        conn.close()
    else:
        village_options = []

    return village_options


# Callback to update options for village dropdown
@dash_app.callback(
    Output('booth-dropdown', 'options'),
    [Input('district-dropdown', 'value'),
     Input('parliamentary-constituency-dropdown', 'value'),
     Input('assembly-constituency-dropdown', 'value'),
     Input('mandal-dropdown', 'value'),
     Input('village-dropdown', 'value')]
)
def update_booth_options(selected_district, selected_pc, selected_ac, selected_mandal, selected_village):
    conn = get_database_connection()
    cursor = conn.cursor()
    if selected_district and selected_district != 'districtall' and selected_pc and selected_pc != 'pcall' and selected_ac != 'acall' and selected_ac and selected_mandal and selected_village:
        # Fetch all distinct villages from the database
        query = """SELECT DISTINCT booth_id, ps_no FROM BLI WHERE district_code = %s AND pc_code = %s and ac_no = %s AND mandal_id = %s AND village_id = %s ORDER BY ps_no;"""

        cursor.execute(query, (selected_district, selected_pc, selected_ac, selected_mandal, selected_village))
        booth_options = [{'label': ps_no, 'value': booth_id} for booth_id, ps_no in cursor.fetchall()]

        cursor.close()
        conn.close()
    elif selected_ac != 'acall' and selected_mandal and selected_village:
        # Fetch all distinct villages from the database
        query = """SELECT DISTINCT booth_id, ps_no FROM BLI WHERE ac_no = %s AND mandal_id = %s AND village_id = %s ORDER BY ps_no;"""

        cursor.execute(query, (selected_ac, selected_mandal, selected_village))
        booth_options = [{'label': ps_no, 'value': booth_id} for booth_id, ps_no in cursor.fetchall()]

        cursor.close()
        conn.close()
    else:
        booth_options = []

    return booth_options


# Callback to update options for sub caste dropdown
@dash_app.callback(
    Output('sub-caste-dropdown', 'options'),
    [Input('caste-dropdown', 'value')]
)
def update_sub_caste_options(selected_caste):
    conn = get_database_connection()
    cursor = conn.cursor()
    if selected_caste is None:
        return [{'label': 'Please Select a Caste', 'value': None}]

    else:
        # Fetch all distinct districts from the database
        query = """SELECT DISTINCT sub_caste, subcaste FROM BLI WHERE caste_id = %s ORDER BY subcaste;"""

        cursor.execute(query, (selected_caste,))
        sub_caste_options = [{'label': subcaste, 'value': sub_caste} for sub_caste, subcaste in cursor.fetchall()]

        cursor.close()
        conn.close()

    return sub_caste_options


@dash_app.callback(
    [Output('voter-pie-chart', 'figure'),
     Output('total-voters', 'children')],
    [
        Input('caste-dropdown', 'value'),
        Input('district-dropdown', 'value'),
        Input('sub-caste-dropdown', 'value'),
        Input('parliamentary-constituency-dropdown', 'value'),
        Input('assembly-constituency-dropdown', 'value'),
        Input('mandal-dropdown', 'value'),
        Input('village-dropdown', 'value'),
        Input('booth-dropdown', 'value'),
    ],
    [State('caste-dropdown', 'options'),
     State('district-dropdown', 'options'),
     State('sub-caste-dropdown', 'options'),
     State('parliamentary-constituency-dropdown', 'options'),
     State('assembly-constituency-dropdown', 'options'),
     State('mandal-dropdown', 'options'),
     State('village-dropdown', 'options'),
     State('booth-dropdown', 'options')]
)
def update_voter_pie_chart(selected_caste, selected_district, selected_sub_caste, selected_pc, selected_ac,
                           selected_mandal,
                           selected_village, selected_booth, caste_option, district_option, sub_caste_option, pc_option,
                           ac_option, mandal_option, village_option, booth_option):
    # Get data based on selected filters
    data = get_data(selected_caste, selected_district, selected_sub_caste, selected_pc, selected_ac, selected_mandal,
                    selected_village, selected_booth)

    # Determine title based on selected filters
    title = generate_title(selected_caste, selected_district, selected_sub_caste, selected_pc, selected_ac,
                           selected_mandal,
                           selected_village, selected_booth, caste_option, district_option, sub_caste_option, pc_option,
                           ac_option, mandal_option, village_option, booth_option)

    # Process data for the pie chart
    df = {
        'Caste': [],
        'NumVoters': [],
        'Color': []
    }

    for row in data:
        if len(row) >= 3:
            if selected_district == "districtall":
                df['Caste'].append(row[1])
                df['NumVoters'].append(int(row[2]))
                df['Color'].extend(get_caste_colors([row[1]]))
            elif selected_pc == "pcall":
                df['Caste'].append(row[1])
                df['NumVoters'].append(int(row[2]))
                df['Color'].extend(get_caste_colors([row[1]]))
            elif selected_ac == 'acall':
                df['Caste'].append(row[1])
                df['NumVoters'].append(int(row[2]))
                df['Color'].extend(get_caste_colors([row[1]]))
        else:
            df['Caste'].append(row[0])
            df['NumVoters'].append(int(row[1]))
            df['Color'].extend(get_caste_colors([row[0]]))

    # Create the pie chart
    fig = go.Figure()

    if data:
        # Add pie chart trace
        fig.add_trace(go.Pie(labels=df['Caste'], values=df['NumVoters'], marker=dict(colors=df['Color']),
                             textinfo='label+percent+value'))

        # Calculate total count
        total_count = sum(df['NumVoters'])

        # Add annotation for total count
        fig.update_layout(
            annotations=[
                dict(
                    text=f'Total Voters: {total_count}',
                    x=0.5,
                    y=1.1,  # Adjust the position as needed
                    showarrow=False,
                    font=dict(family="Arial", size=14, color="RebeccaPurple"),
                )
            ],
            title=dict(
                text=title,
                font=dict(family="Arial", size=14, color="black")
            )
        )
        fig.update_traces(hole=0.3)
        # Serialize figures to JSON format
    return fig, total_count


def generate_title(selected_caste, selected_district, selected_sub_caste, selected_pc, selected_ac, selected_mandal,
                   selected_village, selected_booth,
                   caste_option, district_option, sub_caste_option, pc_option, ac_option, mandal_option, village_option,
                   booth_option):
    labels = []
    values = []

    selected_caste_label = next((option['label'] for option in caste_option if option['value'] == selected_caste), None)
    selected_district_label = next(
        (option['label'] for option in district_option if option['value'] == selected_district), None)
    selected_sub_caste_label = next(
        (option['label'] for option in sub_caste_option if option['value'] == selected_sub_caste), None)
    selected_pc_label = next((option['label'] for option in pc_option if option['value'] == selected_pc), None)
    selected_ac_label = next((option['label'] for option in ac_option if option['value'] == selected_ac), None)
    selected_mandal_label = next((option['label'] for option in mandal_option if option['value'] == selected_mandal),
                                 None)
    selected_village_label = next((option['label'] for option in village_option if option['value'] == selected_village),
                                  None)
    selected_booth_label = next((option['label'] for option in booth_option if option['value'] == selected_booth), None)

    if selected_caste is None:
        labels.append('Caste Breakup')
        values.append('<b style="color:red;">Entire AP</b>')

    if selected_caste:
        labels.append('Caste Breakup</b>')
        values.append('<b style="color:red;">Entire AP</b>')

    if selected_district:
        # Remove "Entire AP" if district is selected
        if '<b style="color:red;">Entire AP</b>' in values:
            index = values.index('<b style="color:red;">Entire AP</b>')
            del values[index]
            del labels[index]
        labels.append('Caste Breakup')
        values.append(f'')

        # Append "Entire AP" if no other value is present
        if not any("Entire AP" in value for value in values):
            labels.append('District')
            values.append(f'<b style="color:red;">{selected_district_label}</b>')

    if selected_pc:
        labels.append('Parliamentary Constituency')
        values.append(f'<b style="color:red;">{selected_pc_label}</b>')

    if selected_ac:
        labels.append('Assembly Constituency')
        values.append(f'<b style="color:red;">{selected_ac_label}</b>')

    if selected_mandal:
        labels.append('Mandal')
        values.append(f'<b style="color:red;">{selected_mandal_label}</b>')

    if selected_village:
        labels.append('Village')
        values.append(f'<b style="color:red;">{selected_village_label}</b>')

    if selected_booth:
        labels.append('Booth')
        values.append(f'<b style="color:red;">{selected_booth_label}</b>')

    title = '<br>'.join([f'{label}: {value}' for label, value in zip(labels, values)])

    return title


def get_caste_colors(caste_list):
    # Assign colors based on caste
    caste_colors = {
        'SC': 'skyblue',
        'ST': 'salmon',
        'BC': 'lightgreen',
        'OC': 'orchid',
        'Others': 'gray'
    }
    # Map each caste to its corresponding color, default to 'black' if not found
    return [caste_colors.get(caste, 'black') for caste in caste_list]


def get_data(selected_caste, selected_district, selected_sub_caste, selected_pc, selected_ac, selected_mandal, selected_village, selected_booth):
    # Define base query
    base_query = """
        SELECT {} 
        FROM BLI 
        WHERE caste not in ('Dead', 'Deleted', 'Not Traced')
    """

    # Add filters based on selected criteria
    filters = []
    params = []

    if selected_district and selected_district != "districtall":
        filters.append("AND district_code = %s")
        params.append(selected_district)

    if selected_pc and selected_pc != "pcall":
        filters.append("AND pc_code = %s")
        params.append(selected_pc)

    if selected_ac and selected_ac != "acall":
        filters.append("AND ac_no = %s")
        params.append(selected_ac)

    if selected_mandal:
        filters.append("AND mandal_id = %s")
        params.append(selected_mandal)

    if selected_village:
        filters.append("AND village_id = %s")
        params.append(selected_village)

    if selected_booth:
        filters.append("AND booth_id = %s")
        params.append(selected_booth)

    # Define selected fields and group by clause based on selections
    selected_fields = "caste, SUM(grand_total) as total_grand_total"
    group_by_clause = "caste"

    if selected_district == "districtall":
        selected_fields = "district_code, caste, SUM(grand_total) as total_grand_total"
        group_by_clause = "district_code, caste"
    elif selected_pc == "pcall":
        selected_fields = "pc_code, caste, SUM(grand_total) as total_grand_total"
        group_by_clause = "pc_code, caste"
    elif selected_ac == "acall":
        selected_fields = "ac_no, caste, SUM(grand_total) as total_grand_total"
        group_by_clause = "ac_no, caste"

    # Construct final query
    final_query = base_query.format(selected_fields) + ' '.join(filters) + f" GROUP BY {group_by_clause};"
    # Execute query
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute(final_query, tuple(params))
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    return data


# Combine the two callbacks into one
@dash_app.callback(
    Output('voter-sub-caste-chart', 'figure'),
    [
        Input('voter-pie-chart', 'clickData'),
        Input('caste-dropdown', 'value'),
        Input('sub-caste-dropdown', 'value'),
        Input('district-dropdown', 'value'),
        Input('parliamentary-constituency-dropdown', 'value'),
        Input('assembly-constituency-dropdown', 'value'),
        Input('mandal-dropdown', 'value'),
        Input('village-dropdown', 'value'),
        Input('booth-dropdown', 'value'),
    ],
    [
        State('caste-dropdown', 'options'),
        State('sub-caste-dropdown', 'options'),
        State('district-dropdown', 'options'),
        State('parliamentary-constituency-dropdown', 'options'),
        State('assembly-constituency-dropdown', 'options'),
        State('mandal-dropdown', 'options'),
        State('village-dropdown', 'options'),
        State('booth-dropdown', 'options'),
        State('total-voters', 'children'),
    ]
)
def update_charts(click_data, selected_caste, selected_sub_caste, selected_district, selected_pc, selected_ac, selected_mandal,
                  selected_village, selected_booth, caste_option, sub_caste_option, district_option, pc_option, ac_option, mandal_option, village_option, booth_option, total_voters):

    # Determine if the total count should be taken from the pie chart or calculated within the function
    voter_sub_caste_chart_figure = update_voter_sub_caste_chart(selected_caste, selected_sub_caste, selected_district,
                                                                selected_pc, selected_ac, selected_mandal, selected_village, selected_booth,
                                                                caste_option, sub_caste_option, district_option,
                                                                pc_option, ac_option, mandal_option, village_option, booth_option, total_voters)

    if dash.callback_context.triggered[0]['prop_id'].split('.')[0] == 'voter-pie-chart':
        click_data = dash.callback_context.triggered[0]['value']
        if click_data:
            # Extract the clicked caste from the stored click data
            clicked_caste = click_data['points'][0]['label']
            # Create a figure for the voter-sub-caste-graph based on the sub-caste data
            voter_sub_caste_chart_figure = create_sub_caste_graph(clicked_caste, selected_district, selected_pc,
                                                                  selected_ac, selected_mandal, selected_village, selected_booth,
                                                                  sub_caste_option, district_option, pc_option,
                                                                  ac_option, mandal_option, village_option, booth_option, total_voters)
            # Return the updated figure
            sub_caste_chart_json = voter_sub_caste_chart_figure.to_json()
            return voter_sub_caste_chart_figure
        else:
            # Handle the case when no click occurs
            pass
    return voter_sub_caste_chart_figure


def update_voter_sub_caste_chart(selected_caste, selected_sub_caste, selected_district, selected_pc, selected_ac,
                                 selected_mandal,
                                 selected_village, selected_booth, caste_option, sub_caste_option, district_option,
                                 pc_option, ac_option, mandal_option, village_option, booth_option, total_voters):
    # Retrieve labels for selected options
    selected_caste_label = next((option['label'] for option in caste_option if option['value'] == selected_caste), None)
    selected_sub_caste_label = next(
        (option['label'] for option in sub_caste_option if option['value'] == selected_sub_caste), None)
    selected_district_label = next(
        (option['label'] for option in district_option if option['value'] == selected_district), None)
    selected_pc_label = next((option['label'] for option in pc_option if option['value'] == selected_pc), None)
    selected_ac_label = next((option['label'] for option in ac_option if option['value'] == selected_ac), None)
    selected_mandal_label = next((option['label'] for option in mandal_option if option['value'] == selected_mandal),
                                 None)
    selected_village_label = next((option['label'] for option in village_option if option['value'] == selected_village),
                                  None)
    selected_booth_label = next((option['label'] for option in booth_option if option['value'] == selected_booth), None)

    # Initialize data and title
    data = []
    title = ''
    total_voters_caste = ''
    voters_total_title = ''
    # Update data and title based on selected options
    if selected_caste and selected_district and selected_pc and selected_ac and selected_mandal and selected_village and selected_booth:
        data = get_sub_caste_byBooth_data(selected_caste, selected_district, selected_pc, selected_ac, selected_mandal,
                                          selected_village, selected_booth)
        title = f'<b style="color:red;">SubCaste Breakup</b> For Caste: <b style="color:red;">{selected_caste_label}</b> Booths: <b style="color:red;">{selected_booth_label}</b>'
        header_label = 'Sub-Caste'
        voters_total_title = 'Booths'
        total_voters_caste = selected_sub_caste_label
    elif selected_sub_caste and selected_caste and selected_district and selected_pc and selected_ac and selected_mandal and selected_village:
        data = get_booth_data(selected_sub_caste, selected_caste, selected_district, selected_pc, selected_ac,
                              selected_mandal, selected_village)
        title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> Villages: <b style="color:red;">{selected_village_label}</b>'
        header_label = 'Booths'
        voters_total_title = 'Booths'
        total_voters_caste = selected_sub_caste_label
    elif selected_sub_caste and selected_caste and selected_district and selected_pc and selected_ac and selected_mandal:
        data = get_village_data(selected_sub_caste, selected_caste, selected_district, selected_pc, selected_ac,
                                selected_mandal)
        title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> Mandals: <b style="color:red;">{selected_mandal_label}</b>'
        header_label = 'Villages'
        voters_total_title = 'Villages'
        total_voters_caste = selected_sub_caste_label
    elif selected_sub_caste and selected_caste and selected_district and selected_pc and selected_ac:
        data = get_mandal_data(selected_sub_caste, selected_caste, selected_district, selected_pc, selected_ac)
        if selected_ac != 'acall':
            title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> Assembly Constituencies: <b style="color:red;">{selected_ac_label}</b>'
            header_label = 'Mandals'
            voters_total_title = 'Mandals'
            total_voters_caste = selected_sub_caste_label
        else:
            title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> Assembly Constituencies: <b style="color:red;">All</b>'
            header_label = 'Assembly Constituencies'
            voters_total_title = 'AC'
            total_voters_caste = selected_sub_caste_label
    elif selected_sub_caste and selected_caste and selected_district and selected_pc and selected_ac:
        data = get_ac_data(selected_sub_caste, selected_caste, selected_district, selected_pc)
        if selected_pc != 'pcall':
            title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> Parliamentary Constituencies: <b style="color:red;">{selected_pc_label}</b>'
            header_label = 'Assembly Constituencies'
            voters_total_title = 'AC'
            total_voters_caste = selected_sub_caste_label
        else:
            title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> Parliamentary Constituencies: <b style="color:red;">All</b>'
            header_label = 'Parliamentary Constituencies'
            voters_total_title = 'PC'
            total_voters_caste = selected_sub_caste_label
    elif selected_sub_caste and selected_caste and selected_district and selected_pc:
        data = get_ac_data(selected_sub_caste, selected_caste, selected_district, selected_pc)
        if selected_pc != 'pcall':
            title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> Parliamentary Constituencies: <b style="color:red;">{selected_pc_label}</b>'
            header_label = 'Assembly Constituencies'
            voters_total_title = 'AC'
            total_voters_caste = selected_sub_caste_label
        else:
            title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> Parliamentary Constituencies: <b style="color:red;">All</b>'
            header_label = 'Parliamentary Constituencies'
            voters_total_title = 'PC'
            total_voters_caste = selected_sub_caste_label
    elif selected_sub_caste and selected_caste and selected_district:
        data = get_pc_data(selected_sub_caste, selected_caste, selected_district)
        title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> District: <b style="color:red;">{selected_district_label}</b>'
        header_label = 'Districts'
        voters_total_title = 'Districts'
        total_voters_caste = selected_sub_caste_label
    elif selected_sub_caste and selected_caste:
        data = get_district_data(selected_sub_caste, selected_caste)
        title = f'<b style="color:red;">SubCaste Breakup</b> For Sub-Caste: <b style="color:red;">{selected_sub_caste_label}</b> District: <b style="color:red;">All</b>'
        header_label = 'Districts'
        voters_total_title = 'Sub-Caste'
        total_voters_caste = selected_sub_caste_label
    elif selected_caste:
        data = get_sub_caste_data_for_caste(selected_caste)
        title = f'<b style="color:red;">SubCaste Breakup</b> For Caste: <b style="color:red;">{selected_caste_label}, Entire AP</b>'
        header_label = 'Sub-Caste'
        voters_total_title = 'All'
        total_voters_caste = selected_sub_caste_label
    else:
        # Provide default data if no filters are selected
        data = []
        title = ''

    # Process data if available
    if data:
        # Sort and convert data to DataFrame
        data = sorted(data, key=lambda x: x[1], reverse=True)
        df = pd.DataFrame(data, columns=[header_label, 'NumVoters'])

        # Calculate percentage
        total_voters_float = float(total_voters)
        # Calculate percentages and convert to strings with two digits after the decimal point
        df['Percentage'] = (df['NumVoters'] / df['NumVoters'].sum() * 100).apply(lambda x: '{:.2f}%'.format(x))
        df['TotalPercentage'] = (df['NumVoters'].astype(float) / total_voters_float * 100).apply(
            lambda x: '{:.2f}%'.format(x))

        # Calculate total number of voters and format it to include in the table
        # total_voters_str = f'Total Voters: {df["NumVoters"].sum()}'
        # total_ap_voters_str = f'Total AP Voters: {total_voters}'
        total_voters_str = f'<b>Total {total_voters_caste}: {df["NumVoters"].sum()}</b>'
        total_ap_voters_str = f'<b>{voters_total_title} Voters: {total_voters}</b>'
        # Create a new row to display the totals
        total_row = pd.DataFrame({header_label: [''],
                                  'NumVoters': [total_voters_str],
                                  'Percentage': [''],
                                  'TotalPercentage': [total_ap_voters_str]})

        # Concatenate the total row with the original DataFrame
        df = pd.concat([total_row, df]).reset_index(drop=True)

        # Remove null values from other columns
        df.fillna('', inplace=True)

        # Create a table without the sequence numbers
        fig = go.Figure(data=[go.Table(
            header=dict(values=[f'<b>{header_label}</b>', '<b>NumVoters</b>', '<b>Percentage</b>',
                                '<b>Percentage of Total AP Voters</b>', '<b>2024 Estimated</b>'],
                        align=['left', 'center', 'center'],
                        font=dict(size=12),  # Adjust header font size
                        height=40,
                        fill=dict(color='lightgray'),
                        line=dict(color='darkslategray', width=2)),
            cells=dict(values=[df[header_label].apply(lambda x: '<b>' + str(x) + '</b>'),
                               df['NumVoters'].astype(str),
                               df['Percentage'],
                               df['TotalPercentage'],
                               ''],
                       align=['left', 'center', 'center'],
                       font=dict(size=10),  # Adjust cell font size
                       height=30,
                       fill=dict(color='white'),
                       line=dict(color='darkslategray', width=1))
        )])

        # Apply CSS styles
        fig.update_layout(
            title=title,
            margin=dict(b=80, t=60, l=40, r=40),
            font=dict(family="Arial", size=12),  # Adjust overall font size
            title_font=dict(family="Arial", size=14, color="black"),
            plot_bgcolor='white',
            paper_bgcolor='white',
            # Increase space between rows
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks='',
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks='',
                showticklabels=False
            ),
            # Make the table responsive
            autosize=True
        )

        # Set the column widths
        column_widths = [0.2, 0.12, 0.12, 0.12, 0.12]  # Adjust as needed

        # Apply the column widths
        fig.update_layout(
            autosize=True,
            template="plotly_white",  # Apply Plotly's white template
            font=dict(family="Arial"),  # Adjust font family
            title_font=dict(size=14),  # Adjust title font size
            margin=dict(l=20, r=65, t=45, b=20),  # Adjust margins
        )

        # Update the table layout with the column widths
        fig.update_traces(columnwidth=column_widths)

        # Return the table figure and a download link for the PDF file
        return fig

    # Return an empty figure if no data is available
    return {}


def get_ac_data_with_caste(selected_district, selected_caste, selected_pc, selected_ac):
    conn = get_database_connection()
    cursor = conn.cursor()
    if selected_caste and selected_district == 'districtall' and selected_pc == 'pcall' and selected_ac == 'acall':
        query = """
            SELECT ac_name, SUM(grand_total) 
            FROM BLI 
            WHERE caste_id = %s
            GROUP BY ac_name;
        """
        cursor.execute(query, (selected_caste, ))
    elif selected_caste and selected_district == 'districtall' and selected_pc == 'pcall' and selected_ac:
        query = """
            SELECT mandal_name, SUM(grand_total) 
            FROM BLI 
            WHERE caste_id = %s AND ac_no = %s
            GROUP BY mandal_name;
        """
        cursor.execute(query, (selected_caste, selected_ac))
    elif selected_caste and selected_district != 'districtall' and selected_pc == 'pcall' and selected_ac == 'acall':
        query = """
            SELECT ac_name, SUM(grand_total) 
            FROM BLI 
            WHERE caste_id = %s AND district_code = %s
            GROUP BY ac_name;
        """
        cursor.execute(query, (selected_caste, selected_pc, selected_district))
    elif selected_caste and selected_district != 'districtall' and selected_pc == 'pcall' and selected_ac:
        query = """
            SELECT mandal_name, SUM(grand_total) 
            FROM BLI 
            WHERE caste_id = %s AND ac_no = %s AND district_code = %s
            GROUP BY mandal_name;
        """
        cursor.execute(query, (selected_caste, selected_pc, selected_district))
    elif selected_caste and selected_district == 'districtall' and selected_pc != 'pcall' and selected_ac:
        query = """
            SELECT mandal_name, SUM(grand_total) 
            FROM BLI 
            WHERE caste_id = %s AND pc_code = %s AND ac_no = %s
            GROUP BY mandal_name;
        """
        cursor.execute(query, (selected_caste, selected_pc, selected_ac))
    else:
        query = """ 
            SELECT mandal_name, SUM(grand_total) 
            FROM BLI 
            WHERE caste_id = %s AND district_code = %s AND pc_code = %s AND ac_no = %s
            GROUP BY mandal_name;
        """
        cursor.execute(query, (selected_caste, selected_district, selected_pc, selected_ac))

    data1 = cursor.fetchall()

    cursor.close()
    conn.close()
    return data1


def get_pc_data_with_caste(selected_district, selected_caste, selected_pc):
    conn = None
    cursor = None
    data1 = []
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        if selected_caste and selected_district == 'districtall' and selected_pc == 'pcall':
            query = """
                SELECT pc_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s
                GROUP BY pc_name;
            """
            cursor.execute(query, (selected_caste, ))
        elif selected_caste and selected_district != 'districtall' and selected_pc == 'pcall':
            query = """
                SELECT pc_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND district_code = %s
                GROUP BY pc_name;
            """
            cursor.execute(query, (selected_caste, selected_district))
        elif selected_caste and selected_district == 'districtall' and selected_pc:
            query = """
                SELECT ac_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND pc_code = %s
                GROUP BY ac_name;
            """
            cursor.execute(query, (selected_caste, selected_pc))
        else:
            query = """ 
                SELECT ac_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND district_code = %s AND pc_code = %s
                GROUP BY ac_name;
            """
            cursor.execute(query, (selected_caste, selected_district, selected_pc))

        data1 = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data1


def get_district_data_with_caste(selected_district, selected_caste):
    conn = None
    cursor = None
    data1 = []
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        if selected_district == 'districtall':
            query = """
                SELECT district_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s
                GROUP BY district_name;
            """
            cursor.execute(query, (selected_caste, ))
        else:
            query = """ 
                SELECT pc_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND district_code = %s
                GROUP BY pc_name;
            """
            cursor.execute(query, (selected_caste, selected_district))

        data1 = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data1


def get_district_data(selected_sub_caste, selected_caste):
    conn = None
    cursor = None
    data1 = []
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        if selected_sub_caste and selected_caste:
            query = """ 
                SELECT district_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s
                GROUP BY district_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste))

        data1 = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data1


def get_pc_data(selected_sub_caste, selected_caste, selected_district):
    conn = None
    cursor = None
    data1 = []

    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        if selected_sub_caste and selected_caste and selected_district == 'districtall':
            query = """
                SELECT district_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s
                GROUP BY district_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste))

        elif selected_sub_caste and selected_caste and selected_district:
            query = """
                SELECT pc_name, SUM(grand_total) 
                FROM BLI 
                WHERE district_code = %s AND caste_id = %s AND sub_caste = %s
                GROUP BY pc_name;
            """
            cursor.execute(query, (selected_district, selected_caste, selected_sub_caste))

        data1 = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data1


def get_ac_data(selected_sub_caste, selected_caste, selected_district, selected_pc):
    conn = None
    cursor = None
    data1 = []

    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        if selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc == 'pcall':
            query = """
                SELECT pc_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s
                GROUP BY pc_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste))
        elif selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc:
            query = """
                SELECT ac_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND pc_code = %s
                GROUP BY ac_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_pc))
        elif selected_sub_caste and selected_caste and selected_district != 'districtall' and selected_pc == 'pcall':
            query = """
                SELECT ac_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND district_code = %s
                GROUP BY ac_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_district))
        elif selected_sub_caste and selected_caste and selected_district and selected_pc:
            query = """
                SELECT ac_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND district_code = %s AND pc_code = %s
                GROUP BY ac_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_district, selected_pc))

        data1 = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data1


def get_mandal_data(selected_sub_caste, selected_caste, selected_district, selected_pc, selected_ac):
    conn = None
    cursor = None
    data1 = []

    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        if selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc == 'pcall' and selected_ac == 'acall':
            query = """
                SELECT ac_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s
                GROUP BY ac_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste))
        elif selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc == 'pcall' and selected_ac:
            query = """
                SELECT mandal_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND ac_no = %s
                GROUP BY mandal_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_ac))
        elif selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc and selected_ac == 'acall':
            query = """
                SELECT ac_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND pc_code = %s
                GROUP BY ac_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_pc))
        elif selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc and selected_ac:
            query = """
                SELECT mandal_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND pc_code = %s AND ac_no = %s
                GROUP BY mandal_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_pc, selected_ac))
        elif selected_sub_caste and selected_caste and selected_district and selected_pc == 'pcall' and selected_ac == 'acall':
            query = """
                SELECT mandal_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND district_code = %s
                GROUP BY mandal_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_district))
        elif selected_sub_caste and selected_caste and selected_district and selected_pc and selected_ac:
            query = """
                SELECT mandal_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND district_code = %s AND pc_code = %s AND ac_no = %s
                GROUP BY mandal_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_district, selected_pc, selected_ac))

        data1 = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data1


def get_village_data(selected_sub_caste, selected_caste, selected_district, selected_pc, selected_ac, selected_mandal):
    conn = None
    cursor = None
    data1 = []

    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        if selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc == 'pcall' and selected_ac and selected_mandal:
            query = """
                SELECT village_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND ac_no = %s AND mandal_id = %s
                GROUP BY village_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_ac, selected_mandal))
        elif selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc and selected_ac and selected_mandal:
            query = """
                SELECT village_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND pc_code = %s AND ac_no = %s AND mandal_id = %s
                GROUP BY village_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_pc, selected_ac, selected_mandal))
        elif selected_sub_caste and selected_caste and selected_district and selected_pc and selected_ac and selected_mandal:
            query = """
                SELECT village_name, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND sub_caste = %s AND district_code = %s AND pc_code = %s AND ac_no = %s AND mandal_id = %s 
                GROUP BY village_name;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_district, selected_pc, selected_ac, selected_mandal))

        data1 = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data1


def get_booth_data(selected_sub_caste, selected_caste, selected_district, selected_pc, selected_ac, selected_mandal, selected_village):
    conn = None
    cursor = None
    data1 = []

    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        if selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc == 'pcall' and selected_ac and selected_mandal and selected_village:
            query = """
                SELECT ps_no, SUM(grand_total) 
                FROM aptomorrow.BLI 
                WHERE caste_id = %s AND sub_caste = %s AND ac_no = %s AND mandal_id = %s AND village_id = %s
                GROUP BY ps_no;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_ac, selected_mandal, selected_village))
        elif selected_sub_caste and selected_caste and selected_district == 'districtall' and selected_pc and selected_ac and selected_mandal and selected_village:
            query = """
                SELECT ps_no, SUM(grand_total) 
                FROM aptomorrow.BLI 
                WHERE caste_id = %s AND sub_caste = %s AND pc_code = %s AND ac_no = %s AND mandal_id = %s AND village_id = %s 
                GROUP BY ps_no;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_pc, selected_ac, selected_mandal, selected_village))
        elif selected_sub_caste and selected_caste and selected_district and selected_pc and selected_ac and selected_mandal and selected_village:
            query = """
                SELECT ps_no, SUM(grand_total) 
                FROM aptomorrow.BLI 
                WHERE caste_id = %s AND sub_caste = %s AND district_code = %s AND pc_code = %s AND ac_no = %s AND mandal_id = %s AND village_id = %s 
                GROUP BY ps_no;
            """
            cursor.execute(query, (selected_caste, selected_sub_caste, selected_district, selected_pc, selected_ac, selected_mandal, selected_village))

        data1 = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data1


def get_sub_caste_byBooth_data(selected_caste, selected_district, selected_pc, selected_ac, selected_mandal, selected_village, selected_booth):
    conn = get_database_connection()
    cursor = conn.cursor()
    data1 = []
    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        if selected_caste and selected_district == 'districtall' and selected_pc == 'pcall' and selected_ac and selected_mandal and selected_village and selected_booth:
            query = """
                SELECT subcaste, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND ac_no = %s AND mandal_id = %s AND village_id = %s AND booth_id = %s  
                AND caste NOT IN ('Dead', 'Deleted', 'Not Traced')
                GROUP BY subcaste;
            """
            cursor.execute(query, (selected_caste, selected_ac, selected_mandal, selected_village, selected_booth))
        elif selected_caste and selected_district == 'districtall' and selected_pc and selected_ac and selected_mandal and selected_village and selected_booth:
            query = """
                SELECT subcaste, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND pc_code = %s AND ac_no = %s AND mandal_id = %s AND village_id = %s AND booth_id = %s  
                AND caste NOT IN ('Dead', 'Deleted', 'Not Traced')
                GROUP BY subcaste;
            """
            cursor.execute(query, (selected_caste, selected_pc, selected_ac, selected_mandal, selected_village, selected_booth))
        elif selected_caste and selected_district and selected_pc and selected_ac and selected_mandal and selected_village and selected_booth:
            query = """
                SELECT subcaste, SUM(grand_total) 
                FROM BLI 
                WHERE caste_id = %s AND district_code = %s AND pc_code = %s AND ac_no = %s AND mandal_id = %s AND village_id = %s AND booth_id = %s  
                AND caste NOT IN ('Dead', 'Deleted', 'Not Traced')
                GROUP BY subcaste;
            """
            cursor.execute(query, (selected_caste, selected_district, selected_pc, selected_ac, selected_mandal, selected_village, selected_booth))

        data1 = cursor.fetchall()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return data1


def get_sub_caste_data_for_caste(selected_caste):
    conn = get_database_connection()
    cursor = conn.cursor()
    if selected_caste:
        query = """
            SELECT subcaste, SUM(grand_total) 
            FROM BLI 
            WHERE caste_id = %s 
            AND caste NOT IN('Dead', 'Deleted', 'Not Traced')
            GROUP BY subcaste;
        """
        cursor.execute(query, (selected_caste, ))

        data1 = cursor.fetchall()

        cursor.close()
        conn.close()
        return data1


def create_sub_caste_graph(clicked_caste, selected_district, selected_pc, selected_ac, selected_mandal,
                           selected_village, selected_booth,
                           sub_caste_option, district_option, pc_option, ac_option, mandal_options, village_option,
                           booth_option, total_voters):
    data1 = []
    title = ''
    total_voters_caste = ''
    voters_total_title = ''
    selected_district_label = next(
        (option['label'] for option in district_option if option['value'] == selected_district), None)
    selected_pc_label = next((option['label'] for option in pc_option if option['value'] == selected_pc), None)
    selected_ac_label = next((option['label'] for option in ac_option if option['value'] == selected_ac), None)
    selected_mandal_label = next((option['label'] for option in mandal_options if option['value'] == selected_mandal),
                                 None)
    selected_village_label = next((option['label'] for option in village_option if option['value'] == selected_village),
                                  None)
    selected_booth_label = next((option['label'] for option in booth_option if option['value'] == selected_booth), None)
    if selected_district and selected_pc and selected_ac and selected_mandal and selected_village and clicked_caste and selected_booth:
        # Display sub_caste-wise count for the selected district,pc,ac,mandal,village, booth and caste
        data1 = get_sub_caste_data(selected_district, selected_pc, selected_ac, selected_mandal, selected_village,
                                   clicked_caste, selected_booth)
        data1 = sorted(data1, key=lambda x: x[1], reverse=True)
        voters_total_title = 'Booth'
        total_voters_caste = clicked_caste
        title = f'<b style="color:red;">SubCaste Breakup</b> for District: <b style="color:red;">{selected_district_label}</b>, PC: <b style="color:red;">{selected_pc_label}</b>,' \
                f' AC: <b style="color:red;">{selected_ac_label}</b>, Mandal: <b style="color:red;">{selected_mandal_label}</b>, Village: <b style="color:red;">{selected_village_label}</b>, Booth: <b style="color:red;">{selected_booth_label}</b>' \
                f' Caste: <b style="color:red;">{clicked_caste}</b>'
    elif selected_district and selected_pc and selected_ac and selected_mandal and selected_village and clicked_caste:
        # Display sub_caste-wise count for the selected district,pc,ac,mandal,village and caste
        data1 = get_sub_caste_data(selected_district, selected_pc, selected_ac, selected_mandal, selected_village,
                                   clicked_caste, None)
        data1 = sorted(data1, key=lambda x: x[1], reverse=True)
        voters_total_title = 'Village'
        total_voters_caste = clicked_caste
        title = f'<b style="color:red;">SubCaste Breakup</b> for District: <b style="color:red;">{selected_district_label}</b>, PC: <b style="color:red;">{selected_pc_label}</b>,' \
                f' AC: <b style="color:red;">{selected_ac_label}</b>, Mandal: <b style="color:red;">{selected_mandal_label}</b>, Village: <b style="color:red;">{selected_village_label}</b>,' \
                f' Caste: <b style="color:red;">{clicked_caste}</b>'
    elif selected_district and selected_pc and selected_ac and selected_mandal and clicked_caste:
        # Display sub_caste-wise count for the selected district,pc,ac,mandal and caste
        data1 = get_sub_caste_data(selected_district, selected_pc, selected_ac, selected_mandal, None, clicked_caste,
                                   None)
        data1 = sorted(data1, key=lambda x: x[1], reverse=True)
        voters_total_title = 'Mandal'
        total_voters_caste = clicked_caste
        title = f'<b style="color:red;">SubCaste Breakup</b> for District: <b style="color:red;">{selected_district_label}</b>, PC: <b style="color:red;">{selected_pc_label}</b>,' \
                f' AC: <b style="color:red;">{selected_ac_label}</b>, Mandal: <b style="color:red;">{selected_mandal_label}</b>, Caste: <b style="color:red;">{clicked_caste}</b>'
    elif selected_district and selected_pc and selected_ac and clicked_caste:
        # Display sub_caste-wise count for the selected district,pc,ac,mandal,caste
        data1 = get_sub_caste_data(selected_district, selected_pc, selected_ac, None, None, clicked_caste, None)
        data1 = sorted(data1, key=lambda x: x[1], reverse=True)
        voters_total_title = 'AC'
        total_voters_caste = clicked_caste
        title = f'<b style="color:red;">SubCaste Breakup</b> for District: <b style="color:red;">{selected_district_label}</b>, PC: <b style="color:red;">{selected_pc_label}</b>,' \
                f' AC: <b style="color:red;">{selected_ac_label}</b>, Caste: <b style="color:red;">{clicked_caste}</b>'
    elif selected_district and selected_pc and clicked_caste:
        # Display sub_caste-wise count for the selected district,pc,ac,mandal,caste
        data1 = get_sub_caste_data(selected_district, selected_pc, None, None, None, clicked_caste, None)
        data1 = sorted(data1, key=lambda x: x[1], reverse=True)
        voters_total_title = 'PC'
        total_voters_caste = clicked_caste
        title = f'<b style="color:red;">SubCaste Breakup</b> for District: <b style="color:red;">{selected_district_label}</b>, PC: <b style="color:red;">{selected_pc_label}</b>,' \
                f' Caste: <b style="color:red;">{clicked_caste}</b>'
    elif selected_district and clicked_caste:
        # Display sub_caste-wise count for the selected district,pc,ac,caste
        data1 = get_sub_caste_data(selected_district, None, None, None, None, clicked_caste, None)
        data1 = sorted(data1, key=lambda x: x[1], reverse=True)
        voters_total_title = 'District'
        total_voters_caste = clicked_caste
        title = f'<b style="color:red;">SubCaste Breakup</b> for District: <b style="color:red;">{selected_district_label}</b>, Caste: <b style="color:red;">{clicked_caste}</b>'
    elif clicked_caste:
        # Display sub_caste-wise count for the selected district,pc,ac,caste
        data1 = get_sub_caste_data(None, None, None, None, None, clicked_caste, None)
        data1 = sorted(data1, key=lambda x: x[1], reverse=True)
        voters_total_title = ''
        total_voters_caste = clicked_caste
        title = f'<b style="color:red;">SubCaste Breakup</b> for Caste: <b style="color:red;">{clicked_caste}, Entire AP</b>'

    df = {
        'Sub-Caste': [row[0] for row in sorted(data1, key=lambda x: x[0], reverse=True)],
        'NumVoters': [row[1] for row in sorted(data1, key=lambda x: x[0], reverse=True)]
    }

    df = pd.DataFrame(data1, columns=['Sub-Caste', 'NumVoters'])
    total_voters_float = float(total_voters)

    # Calculate percentages and convert to strings with two digits after the decimal point
    df['Percentage'] = (df['NumVoters'] / df['NumVoters'].sum() * 100).apply(lambda x: '{:.2f}%'.format(x))
    df['TotalPercentage'] = (df['NumVoters'].astype(float) / total_voters_float * 100).apply(
        lambda x: '{:.2f}%'.format(x))

    # Calculate total number of voters and format it to include in the table
    total_voters_str = f'<b>Total {total_voters_caste}: {df["NumVoters"].sum()}</b>'
    total_ap_voters_str = f'<b>{voters_total_title} Voters: {total_voters}</b>'

    # Create a new row to display the totals
    total_row = pd.DataFrame({'Sub Caste': [''],
                              'NumVoters': [total_voters_str],
                              'Percentage': [''],
                              'TotalPercentage': [total_ap_voters_str]})

    # Concatenate the total row with the original DataFrame
    df = pd.concat([total_row, df]).reset_index(drop=True)

    # Remove null values from other columns
    df.fillna('', inplace=True)
    # Create a table
    sub_caste_fig = go.Figure(data=[go.Table(
        header=dict(values=['Sub Caste', 'NumVoters', 'Percentage', 'Percentage of Total Voters', '2024 Estimated'],
                    align=['left', 'center', 'center'],
                    font=dict(size=14),
                    height=40,
                    fill=dict(color='lightgray'),
                    line=dict(color='darkslategray', width=2)),
        cells=dict(values=[df['Sub-Caste'], df['NumVoters'].astype(str), df['Percentage'], df['TotalPercentage'], ''],
                   align=['left', 'center', 'center'],
                   font=dict(size=12),
                   height=30,
                   fill=dict(color='white'),
                   line=dict(color='darkslategray', width=1)),
    )])

    # Add <colgroup> and <col> elements to adjust column widths
    sub_caste_fig.update_layout(
        title=title,
        margin=dict(b=80, t=60, l=40, r=40),
        font=dict(family="Arial", size=14, color="RebeccaPurple"),
        title_font=dict(family="Arial", size=14, color="black"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        # Increase space between rows
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
    )
    # Set the column widths
    column_widths = [0.2, 0.12, 0.12, 0.12, 0.12]  # Adjust as needed

    # Apply the column widths
    sub_caste_fig.update_layout(
        autosize=True,
        template="plotly_white",  # Apply Plotly's white template
        font=dict(family="Arial"),  # Adjust font family
        title_font=dict(size=14),  # Adjust title font size
        margin=dict(l=20, r=65, t=45, b=20),  # Adjust margins
    )

    # Update the table layout with the column widths
    sub_caste_fig.update_traces(columnwidth=column_widths)
    return sub_caste_fig


def get_sub_caste_data(selected_district, selected_pc, selected_ac, selected_mandal, selected_village, selected_caste, selected_booth):
    # Modify the SQL query based on your database schema and filter conditions
    conn = get_database_connection()
    cursor = conn.cursor()

    # Define the base query
    base_query = """
        SELECT subcaste, SUM(grand_total) 
        FROM BLI 
        WHERE {} 
        AND caste not in('Dead', 'Deleted', 'Not Traced')
        GROUP BY subcaste;
    """

    # Add filters based on selected criteria
    filters = []
    params = []

    if selected_district and selected_district != 'districtall':
        filters.append("district_code = %s")
        params.append(selected_district)

    if selected_pc and selected_pc != 'pcall':
        filters.append("pc_code = %s")
        params.append(selected_pc)

    if selected_ac and selected_ac != 'acall':
        filters.append("ac_no = %s")
        params.append(selected_ac)

    if selected_mandal:
        filters.append("mandal_id = %s")
        params.append(selected_mandal)

    if selected_village:
        filters.append("village_id = %s")
        params.append(selected_village)

    if selected_caste:
        filters.append("caste = %s")
        params.append(selected_caste)

    if selected_booth:
        filters.append("booth_id = %s")
        params.append(selected_booth)

    where_clause = " AND ".join(filters)
    final_query = base_query.format(where_clause)

    cursor.execute(final_query, tuple(params))
    data1 = cursor.fetchall()

    cursor.close()
    conn.close()
    return data1


# Callback to reset dropdown values
@dash_app.callback(
    [
        Output('district-dropdown', 'value'),
        Output('parliamentary-constituency-dropdown', 'value'),
        Output('assembly-constituency-dropdown', 'value'),
        Output('mandal-dropdown', 'value'),
        Output('village-dropdown', 'value'),
        Output('booth-dropdown', 'value'),
        Output('caste-dropdown', 'value'),
        Output('sub-caste-dropdown', 'value'),
    ],
    [
        Input('reset-button', 'n_clicks'),
    ]
)
def reset_dropdown_values(n_clicks):
    # Use the number of clicks to trigger the reset
    if n_clicks > 0:
        return [None] * 8  # Reset all dropdown values
    else:
        # Return the current values
        return [
            dash.callback_context.triggered_id,  # Return the dummy trigger to avoid NoneType error
            dash.callback_context.triggered_id,
            dash.callback_context.triggered_id,
            dash.callback_context.triggered_id,
            dash.callback_context.triggered_id,
            dash.callback_context.triggered_id,
            dash.callback_context.triggered_id,
            dash.callback_context.triggered_id,
        ]


# Define an empty div for the dynamic title
dynamic_title = html.Div(id='dynamic-title', style={'backgroundColor': 'white', 'color': 'black'})
# Define the layout of the dashboard
dash_app1.layout = html.Div(style={'backgroundColor': '#f2f2f2'}, children=[
    dcc.Location(id='dash-url', refresh=False),
    html.Div(id='total-polling-voters', style={'display': 'none'}),
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Polling and Demographic Analysis", className="mb-2", style={'color': 'blue'})),
            dbc.Col(html.Div(id='welcome-message1', children=[], style={'text-align': 'right', 'font-size': '18px'}))
        ]),
        dbc.Row([
            dbc.Col([], width={"size": 6, "order": "first"}),  # Empty column to push elements to the right
            dbc.Col(html.A("Dashboard", href="/dashboard", style={'color': 'red'}),
                    width={"size": 2, "order": "last", "offset": 0}, lg=2, md=3, sm=4, xs=12),
            dbc.Col(html.A("Logout", href="/logout", style={'color': 'orange'}),
                    width={"size": 2, "order": "last", "offset": 0}, lg=2, md=3, sm=4, xs=12),
            dbc.Col(html.Button('Reset', id='reset-button1', n_clicks=0, style={'color': 'blue'}),
                    width={"size": 2, "order": "last", "offset": 0}, lg=2, md=3, sm=4, xs=12),
            html.Button('Print as a PDF', id='download-pdf-button1', className='btn btn-link text-primary',
                        style={'textDecoration': 'none'}),
            html.Div(id='dummy-output1', style={'display': 'none'})
        ]),

        dbc.Row([
            dbc.Col([
                html.Label("Parliamentary Constituencies:"),
                dcc.Dropdown(
                    id='polling-parliamentary-constituency-dropdown',
                    options=[],  # Will be populated dynamically
                    multi=False,
                    value=None,
                    placeholder="Select Parliamentary Constituency",
                    style=dropdown_style,
                ),
            ], width=3),
            dbc.Col([
                html.Label("Assembly Constituencies:"),
                dcc.Dropdown(
                    id='polling-assembly-constituency-dropdown',
                    options=[],  # Will be populated dynamically
                    multi=False,
                    value=None,
                    placeholder="Select Assembly Constituency",
                    style=dropdown_style,
                ),
            ], width=3),
            dbc.Col([
                html.Label("Mandals:"),
                dcc.Dropdown(
                    id='polling-mandal-dropdown',
                    options=[],  # Will be populated dynamically
                    multi=False,
                    value=None,
                    placeholder="Select Mandal",
                    style=dropdown_style,
                ),
            ], width=2),
            dbc.Col([
                html.Label("Polling Village:"),
                dcc.Dropdown(
                    id='polling-village-dropdown',
                    options=[],  # Will be populated dynamically
                    multi=False,
                    value=None,
                    placeholder="Select Village",
                    style=dropdown_style,
                ),
            ], width=2),
            dbc.Col([
                html.Label("Polling Caste:"),
                dcc.Dropdown(
                    id='polling-caste-dropdown',
                    options=[],  # Will be populated dynamically
                    multi=False,
                    value=None,
                    placeholder="Select Caste",
                    style=dropdown_style,
                ),
            ], width=2),
        ], className="mb-1"),
        # Place the dynamic title here, above the row of charts
        dynamic_title,
        dbc.Row([
            dbc.Col([], width=12),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                html.H5(children=[html.B("Polling Trends")], style={'text-align': 'center'}),
                dcc.Graph(id='polling-analysis-chart', className="mt-4", style={'height': '400px', 'width': '100%'}),
            ], width={"size": 12, "order": "first", "offset": 0}, lg=6, md=12, sm=12, xs=12),
            dbc.Col([
                html.H5(children=[html.B("2019 Caste Breakup")], style={'text-align': 'center'}),
                dcc.Graph(id='polling-pie-chart', className="mt-4", style={'height': '400px'}),
            ], width={"size": 12, "order": "middle", "offset": 0}, lg=3, md=12, sm=12, xs=12),
            dbc.Col([
                html.H5(children=[html.B("2024 Age Group Breakup")], style={'text-align': 'center'}),
                dcc.Graph(id='age-group-pie-chart', className="mt-4", style={'height': '400px'}),
            ], width={"size": 12, "order": "last", "offset": 0}, lg=3, md=12, sm=12, xs=12),
        ], ),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='sub-caste-polling-chart', className="mt-4", style={'height': '500px'}),
            ], width={"size": 12, "order": "first", "offset": 0}, lg=12, md=12, sm=12, xs=12),
        ], className="mb-1"),
    ], fluid=True)
])

# JavaScript to trigger print when the button is clicked
dash_app1.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            var buttonsToHide = document.querySelectorAll('.btn, #reset-button1');
            buttonsToHide.forEach(function(button) {
                button.style.display = 'none';
            });
            // Hide labels and dropdowns
            var labelsAndDropdowns = document.querySelectorAll('label, select');
            labelsAndDropdowns.forEach(function(element) {
                element.style.display = 'none';
            });

            // Hide the print as PDF row
            var welcomeMessage = document.querySelector('#welcome-message1');
            if (welcomeMessage) {
                welcomeMessage.style.display = 'none';
            }
            var printButtonRow = document.querySelector('#polling-parliamentary-constituency-dropdown');
            if (printButtonRow) {
                printButtonRow.style.display = 'none';
            }
            var printButtonRow1 = document.querySelector('#polling-assembly-constituency-dropdown');
            if (printButtonRow1) {
                printButtonRow1.style.display = 'none';
            }
            var printButtonRow2 = document.querySelector('#polling-mandal-dropdown');
            if (printButtonRow2) {
                printButtonRow2.style.display = 'none';
            }
            var printButtonRow3 = document.querySelector('#polling-village-dropdown');
            if (printButtonRow3) {
                printButtonRow3.style.display = 'none';
            }
            var printButtonRow4 = document.querySelector('#polling-caste-dropdown');
            if (printButtonRow4) {
                printButtonRow4.style.display = 'none';
            }
            // Hide Dashboard and Logout links
            var dashboardLink = document.querySelector('a[href="/dashboard"]');
            if (dashboardLink) {
                dashboardLink.style.display = 'none';
            }
            var logoutLink = document.querySelector('a[href="/logout"]');
            if (logoutLink) {
                logoutLink.style.display = 'none';
            }

            // Adjust the width of the polling analysis chart
            var pollingAnalysisChart = document.querySelector('#polling-analysis-chart');
            if (pollingAnalysisChart) {
                pollingAnalysisChart.style.width = '100%';
            }

            // Introduce a delay before printing
            setTimeout(function() {
                // Print the window
                window.print();

                // Show labels, dropdowns, Dashboard, Logout, and the print as PDF row again after printing
                labelsAndDropdowns.forEach(function(element) {
                    element.style.display = '';
                });
                buttonsToHide.forEach(function(button) {
                    button.style.display = '';
                });
                if (printButtonRow) {
                    printButtonRow.style.display = '';
                }
                if (printButtonRow1) {
                    printButtonRow1.style.display = '';
                }
                if (printButtonRow2) {
                    printButtonRow2.style.display = '';
                }
                if (printButtonRow3) {
                    printButtonRow3.style.display = '';
                }
                if (printButtonRow4) {
                    printButtonRow4.style.display = '';
                }
                if (dashboardLink) {
                    dashboardLink.style.display = '';
                }
                if (logoutLink) {
                    logoutLink.style.display = '';
                }
                if (welcomeMessage1) {
                    welcomeMessage1.style.display = '';
                }
            }, 500); // Adjust the delay time as needed
        }
    }
    """,
    Output('dummy-output1', 'children'),
    [Input('download-pdf-button1', 'n_clicks')]
)


# Callback to update the welcome message
@dash_app.callback(
    Output('welcome-message1', 'children'),
    [Input('dash-url', 'pathname')]
)
def update_welcome_message(pathname):
    if 'logged_in' in session and session['logged_in']:
        return html.Div([
            html.H3(f"Welcome, {session['0']}! | "),
        ])
    return ''


# Callback to update the welcome message
@dash_app1.callback(
    Output('welcome-message1', 'children'),
    [Input('polling-dash-url', 'pathname')]
)
def update_welcome_message(pathname):
    if 'logged_in' in session and session['logged_in']:
        return html.Div([
            html.H3(f"Welcome, {session['username']}! | "),
        ])
    return ''


# Callback to reset dropdown values
@dash_app1.callback(
    [
        Output('polling-parliamentary-constituency-dropdown', 'value'),
        Output('polling-assembly-constituency-dropdown', 'value'),
        Output('polling-mandal-dropdown', 'value'),
        Output('polling-village-dropdown', 'value'),
        Output('polling-caste-dropdown', 'value'),
    ],
    [
        Input('reset-button1', 'n_clicks'),
    ]
)
def reset_dropdown_values(n_clicks):
    # Use the number of clicks to trigger the reset
    if n_clicks > 0:
        return [None] * 5  # Reset all dropdown values
    else:
        # Return the current values
        return [
            dash.callback_context.triggered_id,  # Return the dummy trigger to avoid NoneType error
            dash.callback_context.triggered_id,
            dash.callback_context.triggered_id,
            dash.callback_context.triggered_id,
            dash.callback_context.triggered_id,
        ]


# Callback to update options for PC dropdown
@dash_app1.callback(
    Output('polling-assembly-constituency-dropdown', 'options'),
    [Input('polling-parliamentary-constituency-dropdown', 'value')]
)
def update_polling_assembly_constituencies(selected_parliamentary_constituency):
    conn = get_database_connection()
    cursor = conn.cursor()

    # Fetch all distinct assembly constituencies from the database for the selected parliamentary constituency
    query = """SELECT DISTINCT ac_code,assembly FROM apt_20141019_polling_data_all_constituencies WHERE pc_code = %s ORDER BY assembly;"""
    cursor.execute(query, (selected_parliamentary_constituency,))
    polling_ac_options = [{'label': f'{assembly} ({ac_code})', 'value': ac_code} for ac_code, assembly in
                          cursor.fetchall()]

    cursor.close()
    conn.close()

    return polling_ac_options


# Callback to update options for PC dropdown based on selected value
@dash_app1.callback(
    Output('polling-parliamentary-constituency-dropdown', 'options'),
    [Input('polling-parliamentary-constituency-dropdown', 'value')]
)
def update_polling_parliamentary_constituencies(selected_parliamentary_constituency):
    conn = get_database_connection()
    cursor = conn.cursor()

    # Fetch all distinct parliamentary constituencies from the database
    query = """SELECT DISTINCT pc_code,parliament FROM apt_20141019_polling_data_all_constituencies ORDER BY parliament;"""
    cursor.execute(query)
    polling_pc_options = [{'label': f'{parliament} ({pc_code})', 'value': pc_code} for pc_code, parliament in
                          cursor.fetchall()]

    cursor.close()
    conn.close()

    return polling_pc_options


# Callback to update options for Mandal dropdown based on selected AC
@dash_app1.callback(
    Output('polling-mandal-dropdown', 'options'),
    [Input('polling-assembly-constituency-dropdown', 'value'),
     Input('polling-parliamentary-constituency-dropdown', 'value')]
)
def update_polling_mandal(selected_polling_constituency, selected_parliamentary_const):
    conn = get_database_connection()
    cursor = conn.cursor()
    # Fetch all distinct polling villages from the database
    query = """SELECT DISTINCT mandalortown FROM apt_20141019_polling_data_all_constituencies WHERE pc_code = %s AND ac_code=%s ORDER BY mandalortown;"""
    cursor.execute(query, (selected_parliamentary_const, selected_polling_constituency))
    polling_mandal_options = [{'label': mandalortown, 'value': mandalortown} for mandalortown in
                              cursor.fetchall()]
    print(polling_mandal_options)
    cursor.close()
    conn.close()

    return polling_mandal_options


# Callback to update options for polling village dropdown
@dash_app1.callback(
    Output('polling-village-dropdown', 'options'),
    [Input('polling-assembly-constituency-dropdown', 'value'),
     Input('polling-parliamentary-constituency-dropdown', 'value'),
     Input('polling-mandal-dropdown', 'value')]
)
def update_polling_village(selected_polling_constituency, selected_parliamentary_const, selected_mandal):
    conn = get_database_connection()
    selected_mandal = selected_mandal[0] if selected_mandal else None
    cursor = conn.cursor()
    # Fetch all distinct polling villages from the database
    query = """SELECT DISTINCT village FROM apt_20141019_polling_data_all_constituencies WHERE pc_code = %s AND ac_code=%s AND mandalortown = %s ORDER BY village;"""
    cursor.execute(query, (selected_parliamentary_const, selected_polling_constituency, selected_mandal))
    polling_village_options = [{'label': village, 'value': village} for village in
                               cursor.fetchall()]

    cursor.close()
    conn.close()

    return polling_village_options


# Callback to update options for polling constituency dropdown
@dash_app1.callback(
    Output('polling-caste-dropdown', 'options'),
    [Input('polling-parliamentary-constituency-dropdown', 'value')]
)
def update_polling_caste(selected_polling_constituency):
    conn = get_database_connection()
    cursor = conn.cursor()
    # Fetch all distinct polling caste from the database
    query = """SELECT DISTINCT caste FROM BLI WHERE pc_code=%s AND caste not in('Dead', 'Deleted', 'Not Traced') ORDER BY caste;"""
    cursor.execute(query, (selected_polling_constituency,))

    polling_caste_options = [{'label': caste, 'value': caste} for caste in cursor.fetchall()]

    polling_caste_options.insert(0, {'label': 'All', 'value': 'casteall'})

    cursor.close()
    conn.close()

    return polling_caste_options


# Callback to update the bar chart based on filter selections
@dash_app1.callback(
    [
        Output('dynamic-title', 'children'),
        Output('polling-pie-chart', 'figure'),
        Output('polling-analysis-chart', 'figure'),
        Output('age-group-pie-chart', 'figure'),
        Output('total-polling-voters', 'children'),
    ],
    [
        Input('polling-parliamentary-constituency-dropdown', 'value'),
        Input('polling-assembly-constituency-dropdown', 'value'),
        Input('polling-mandal-dropdown', 'value'),
        Input('polling-village-dropdown', 'value'),
    ],
    [State('polling-parliamentary-constituency-dropdown', 'options'),
     State('polling-assembly-constituency-dropdown', 'options')]
)
def update_polling_charts(selected_pc, selected_ac, selected_mandal, selected_polling_village, pcoptions, acoptions):
    pie_chart_fig = []
    analysis_chart_fig = []
    age_group_pie_chart_fig = []
    total_count = ''
    title = ''
    selected_pc_label = next((option['label'] for option in pcoptions if option['value'] == selected_pc), None)
    selected_ac_label = next((option['label'] for option in acoptions if option['value'] == selected_ac), None)

    if selected_pc and selected_ac and selected_mandal and selected_polling_village:
        mandal_str = ', '.join(map(str, selected_mandal)) if selected_mandal else ""
        village_str = ', '.join(map(str, selected_polling_village)) if selected_polling_village else ""
        title = html.Div([
            html.Span(f'Charts for PC: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(selected_pc_label, style={'color': 'red', 'font-weight': 'bold'}),
            html.Span(f', AC: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(selected_ac_label, style={'color': 'red', 'font-weight': 'bold'}),
            html.Span(f', Mandal: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(mandal_str, style={'color': 'red', 'font-weight': 'bold'}),
            html.Span(f', Village: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(village_str, style={'color': 'red', 'font-weight': 'bold'})
        ])
        # Update polling pie chart based on selected pc, ac, mandal and village
        pie_chart_fig, total_count = update_pie_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac,
                                                      selected_mandal, selected_polling_village)

        # Update polling analysis chart based on selected pc, ac, mandal and village
        analysis_chart_fig = update_analysis_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac,
                                                   selected_mandal, selected_polling_village)

        # Update polling analysis chart based on selected pc, ac, mandal and village
        age_group_pie_chart_fig = update_age_group_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac,
                                                         selected_mandal, selected_polling_village)

    elif selected_pc and selected_ac and selected_mandal:
        mandal_str = ', '.join(map(str, selected_mandal)) if selected_mandal else ""
        title = html.Div([
            html.Span(f'Charts for PC: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(selected_pc_label, style={'color': 'red', 'font-weight': 'bold'}),
            html.Span(f', AC: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(selected_ac_label, style={'color': 'red', 'font-weight': 'bold'}),
            html.Span(f', Mandal: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(mandal_str, style={'color': 'red', 'font-weight': 'bold'})
        ])
        # Update polling pie chart based on selected pc, ac, mandal
        pie_chart_fig, total_count = update_pie_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac,
                                                      selected_mandal, None)

        # Update polling analysis chart based on selected pc, ac, mandal
        analysis_chart_fig = update_analysis_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac,
                                                   selected_mandal, None)

        # Update polling pie chart based on selected pc, ac, mandal
        age_group_pie_chart_fig = update_age_group_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac,
                                                         selected_mandal, None)

    elif selected_pc and selected_ac:
        title = html.Div([
            html.Span(f'Charts for PC: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(selected_pc_label, style={'color': 'red', 'font-weight': 'bold'}),
            html.Span(f', AC: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(selected_ac_label, style={'color': 'red', 'font-weight': 'bold'})
        ])
        # Update polling pie chart based on selected pc, ac
        pie_chart_fig, total_count = update_pie_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac,
                                                      None, None)

        # Update polling analysis chart based on selected pc, ac
        analysis_chart_fig = update_analysis_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac, None,
                                                   None)

        # Update polling pie chart based on selected pc, ac
        age_group_pie_chart_fig = update_age_group_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac,
                                                         None, None)

    elif selected_pc:
        title = html.Div([
            html.Span(f'Charts for PC: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(selected_pc_label, style={'color': 'red', 'font-weight': 'bold'}),
        ])
        # Update polling pie chart based on selected pc
        pie_chart_fig, total_count = update_pie_chart(selected_pc_label, selected_ac_label, selected_pc, None, None,
                                                      None)

        # Update polling analysis chart based on selected pc
        analysis_chart_fig = update_analysis_chart(selected_pc_label, selected_ac_label, selected_pc, None, None, None)

        # Update polling pie chart based on selected pc
        age_group_pie_chart_fig = update_age_group_chart(selected_pc_label, selected_ac_label, selected_pc, None, None,
                                                         None)

    elif selected_ac:
        title = html.Div([
            html.Span(f'Charts for AC: ', style={'color': 'black', 'font-weight': 'bold'}),
            html.Span(selected_ac_label, style={'color': 'red', 'font-weight': 'bold'}),
        ])
        # Update polling pie chart based on selected ac
        pie_chart_fig, total_count = update_pie_chart(selected_pc_label, selected_ac_label, None, selected_ac, None,
                                                      None)

        # Update polling analysis chart based on selected ac
        analysis_chart_fig = update_analysis_chart(selected_pc_label, selected_ac_label, None, selected_ac, None, None)

        # Update polling pie chart based on selected pc, ac, mandal
        age_group_pie_chart_fig = update_age_group_chart(selected_pc_label, selected_ac_label, None, selected_ac, None,
                                                         None)
    if total_count:
        return title, pie_chart_fig, analysis_chart_fig, age_group_pie_chart_fig, total_count
    else:
        return title, pie_chart_fig, analysis_chart_fig, age_group_pie_chart_fig, 0


# Placeholder function for updating pie chart
def update_pie_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac, selected_mandal,
                     selected_polling_village):
    total_count = 0
    if selected_pc and selected_ac and selected_mandal and selected_polling_village:
        data = get_polling_data(selected_pc, selected_ac, selected_mandal, selected_polling_village)
        mandal_str = ', '.join(map(str, selected_mandal)) if selected_mandal else ""
        village_str = ', '.join(map(str, selected_polling_village)) if selected_polling_village else ""
    elif selected_pc and selected_ac and selected_mandal:
        data = get_polling_data(selected_pc, selected_ac, selected_mandal, None)
        mandal_str = ', '.join(map(str, selected_mandal)) if selected_mandal else ""
    elif selected_pc and selected_ac:
        data = get_polling_data(selected_pc, selected_ac, None, None)
    elif selected_pc:
        data = get_polling_data(selected_pc, None, None, None)
    elif selected_ac:
        data = get_polling_data(None, selected_ac, None, None)

    df = {
        'Caste': [row[0] for row in data],
        'NumVoters': [row[1] for row in data],
        'Color': get_caste_colors([row[0] for row in data])  # Use a function to get caste-specific colors
    }
    fig = go.Figure()
    if data:
        # Add pie chart trace
        fig.add_trace(go.Pie(labels=df['Caste'], values=df['NumVoters'], marker=dict(colors=df['Color']),
                             textinfo='label+percent+value', showlegend=False))

        # Calculate total count
        total_count = sum(df['NumVoters'])

        # Add annotation for total count
        fig.update_layout(
            annotations=[
                dict(
                    text=f'',
                    # text=f'Total Voters: {total_count}',
                    x=1.0,
                    y=1.4,  # Adjust the position as needed
                    showarrow=False,
                    font=dict(family="Arial", size=20, color="RebeccaPurple"),
                ),
                # dict(
                #    text="<b>Caste-Breakup:</b>",  # Title for the chart
                #    x=-0.25,
                #    y=1.4,  # Adjusted position of the title annotation
                #    showarrow=False,
                #    font=dict(family="Arial", size=14, color="black"),
                # )
            ]
        )
        fig.update_traces(hole=0.2)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

    return fig, total_count


def get_party_color(party):
    party_lower = party.lower()
    if '2014_tdp' in party_lower or '2014_tdpmajority' in party_lower or '2019_tdp_majority' in party_lower or '2019_tdp' in party_lower:
        return 'gold'
    elif '2014_ycp' in party_lower or '2019_ycp' in party_lower:
        return 'skyblue'
    else:
        return 'gray'


def update_analysis_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac, selected_mandal,
                          selected_polling_village):
    data1 = get_polling_bar_chart_data(selected_pc, selected_ac, selected_mandal, selected_polling_village)
    mandal_str = ', '.join(map(str, selected_mandal)) if selected_mandal else ""
    village_str = ', '.join(map(str, selected_polling_village)) if selected_polling_village else ""

    df = pd.DataFrame(data1,
                      columns=['2014_tdp', '2014_ycp', '2014_tdpmajority', '2019_tdp', '2019_ycp', '2019_tdp_majority'])

    # Check if the DataFrame is not empty
    if not df.empty:
        # Transpose the DataFrame to have a single row with multiple columns
        df_transposed = df.T.reset_index()

        # Rename columns for better display names
        df_transposed = df_transposed.rename(columns={
            '2014_tdp': 'TDP',
            '2014_ycp': 'YCP',
            '2014_tdpmajority': 'TDP Majority',
            '2019_tdp': 'TDP',
            '2019_ycp': 'YCP',
            '2019_tdp_majority': 'TDP Majority'
        })

        # Create subplots for 2014 and 2019 with taller subplot_titles
        fig = make_subplots(
            rows=1, cols=2,
            shared_yaxes=True,
            vertical_spacing=0.1,
            horizontal_spacing=0.1,
            column_widths=[0.2, 0.2]
        )

        # Mapping between original column names and display names
        column_mapping = {
            '2014_tdp': 'TDP',
            '2014_ycp': 'YCP',
            '2014_tdpmajority': 'TDP Majority',
            '2019_tdp': 'TDP',
            '2019_ycp': 'YCP',
            '2019_tdp_majority': 'TDP Majority'
        }

        # Iterate over each party and add a bar to the corresponding subplot
        for i, year in enumerate(['2014', '2019'], start=1):
            year_columns = [f'{year}_tdp', f'{year}_ycp', f'{year}_tdpmajority', f'{year}_tdp_majority']
            year_data = df_transposed[df_transposed['index'].isin(year_columns)]

            # Add a bar chart for the specific year
            for index, row in year_data.iterrows():
                party = row['index']
                display_name = column_mapping.get(party,
                                                  party)  # Use display name if available, otherwise use original name
                votes = row[0]

                color = get_party_color(party)

                # Add the bar to the subplot
                fig.add_trace(go.Bar(
                    x=[display_name],  # Use display name instead of original name
                    y=[votes],
                    marker=dict(color=color),
                    width=0.2,
                    showlegend=False
                ), row=1, col=i)

                # Add annotation above each bar
                fig.add_annotation(
                    x=display_name,  # Use display name instead of original name
                    y=int(votes) + 5,
                    text=str(votes),
                    showarrow=False,
                    row=1,
                    col=i,
                    yshift=10
                )

            # Add title annotations at the bottom of each graph
            title_annotation_height = df_transposed[0].max() - 10  # Adjust as needed

            fig.add_annotation(
                x=0.5,
                y=title_annotation_height,
                text=f'<b>{str(year)}</b>',
                showarrow=False,
                font=dict(size=16),
                xref=f'x{i}',
                yref=f'y{i}',
                row=1,
                col=i,
                yshift=30  # Adjust this value to move the titles higher
            )

        # Update layout
        fig.update_layout(
            barmode='group',
            showlegend=False,
            font=dict(family="Arial", size=14, color="RebeccaPurple"),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                showline=True,
                linecolor='black',
                linewidth=2,
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=2,
            ),
            margin=dict(t=100, l=40, r=40),  # Adjusted left and right margins
            xaxis2=dict(
                showgrid=True,
                gridcolor='lightgray',
                showline=True,
                linecolor='black',
                linewidth=2,
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=2,
            ),
            # title="<b>Polling-Trends:</b>",  # Title for the chart
            # title_font=dict(family="Arial", size=14, color="black"),  # Font style for the title
        )

        # Find the minimum and maximum values for the entire DataFrame
        min_value = df_transposed[0].min()
        max_value = df_transposed[0].max()

        # Iterate over each subplot and set the y-axis range
        for i in range(1, 3):  # Assuming you have 2 subplots
            fig.update_yaxes(range=[min_value - 10, max_value + 10], zeroline=True, zerolinecolor='black',
                             zerolinewidth=2, row=1, col=i)
            fig.update_xaxes(showgrid=True, gridcolor='lightgray', showline=True, linecolor='black', linewidth=2, row=1,
                             col=i)
            fig.update_yaxes(showgrid=True, gridcolor='lightgray', showline=True, linecolor='black', linewidth=2, row=1,
                             col=i)

    else:
        # Handle the case when the DataFrame is empty
        fig = go.Figure()

    return fig


def get_polling_data(selected_pc, selected_ac, selected_mandal, selected_polling_village):
    polling_data = []
    try:
        conn = get_database_connection()
        selected_polling_village = selected_polling_village[0] if selected_polling_village else None
        selected_mandal = selected_mandal[0] if selected_mandal else None

        with conn.cursor() as cursor:
            # Modify the SQL query based on your database schema and filter conditions
            if selected_pc and selected_ac and selected_mandal and selected_polling_village:
                query = """
                    SELECT caste, SUM(grand_total) 
                    FROM BLI 
                    WHERE pc_code = %s AND ac_no = %s AND mandal_name = %s AND village_name = %s AND caste NOT IN ('Dead', 'Deleted', 'Not Traced')
                    GROUP BY caste;
                """
                cursor.execute(query, (selected_pc, selected_ac, selected_mandal, selected_polling_village))
            elif selected_pc and selected_ac and selected_mandal:
                query = """
                    SELECT caste, SUM(grand_total) 
                    FROM BLI 
                    WHERE pc_code = %s AND ac_no = %s AND mandal_name = %s AND caste NOT IN ('Dead', 'Deleted', 'Not Traced')
                    GROUP BY caste;
                """
                cursor.execute(query, (selected_pc, selected_ac, selected_mandal))
            elif selected_pc and selected_ac:
                query = """
                    SELECT caste, SUM(grand_total) 
                    FROM BLI 
                    WHERE pc_code = %s AND ac_no = %s AND caste NOT IN ('Dead', 'Deleted', 'Not Traced')
                    GROUP BY caste;
                """
                cursor.execute(query, (selected_pc, selected_ac))
            elif selected_pc:
                query = """
                    SELECT caste, SUM(grand_total) 
                    FROM BLI 
                    WHERE pc_code = %s AND caste NOT IN ('Dead', 'Deleted', 'Not Traced')
                    GROUP BY caste;
                """
                cursor.execute(query, (selected_pc, ))
            elif selected_ac:
                query = """
                    SELECT caste, SUM(grand_total) 
                    FROM BLI 
                    WHERE ac_no = %s AND caste NOT IN ('Dead', 'Deleted', 'Not Traced')
                    GROUP BY caste;
                """
                cursor.execute(query, (selected_ac,))

            polling_data = cursor.fetchall()

        return polling_data

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        if conn:
            conn.close()


def get_polling_bar_chart_data(selected_pc, selected_ac, selected_mandal, selected_polling_village):
    polling_data = []
    try:
        conn = get_database_connection()
        selected_polling_village = selected_polling_village[0] if selected_polling_village else None
        selected_mandal = selected_mandal[0] if selected_mandal else None
        with conn.cursor() as cursor:
            # Modify the SQL query based on your database schema and filter conditions
            if selected_pc and selected_ac and selected_mandal and selected_polling_village:
                query = """
                    SELECT SUM("tdp2014") as "2014_tdp", SUM("ysrcp2014") as "2014_ycp", SUM("tdp_ycp_diff2014") as "2014_tdpmajority", SUM("tdp2019") as "2019_tdp", SUM("ysrcp2019") as "2019_ycp", SUM("tdp_ycp_diff2019") as "2019_tdp_majority"
                    FROM apt_20141019_polling_data_all_constituencies
                    WHERE pc_code = %s AND ac_code = %s AND mandalortown = %s AND village = %s;
                """
                cursor.execute(query, (selected_pc, selected_ac, selected_mandal, selected_polling_village))
            elif selected_pc and selected_ac and selected_mandal:
                query = """
                    SELECT SUM("tdp2014") as "2014_tdp", SUM("ysrcp2014") as "2014_ycp", SUM("tdp_ycp_diff2014") as "2014_tdpmajority", SUM("tdp2019") as "2019_tdp", SUM("ysrcp2019") as "2019_ycp", SUM("tdp_ycp_diff2019") as "2019_tdp_majority"
                    FROM apt_20141019_polling_data_all_constituencies
                    WHERE pc_code = %s AND ac_code = %s AND mandalortown = %s;
                """
                cursor.execute(query, (selected_pc, selected_ac, selected_mandal))
            elif selected_pc and selected_ac:
                query = """
                    SELECT SUM("tdp2014") as "2014_tdp", SUM("ysrcp2014") as "2014_ycp", SUM("tdp_ycp_diff2014") as "2014_tdpmajority", SUM("tdp2019") as "2019_tdp", SUM("ysrcp2019") as "2019_ycp", SUM("tdp_ycp_diff2019") as "2019_tdp_majority"
                    FROM apt_20141019_polling_data_all_constituencies
                    WHERE pc_code = %s AND ac_code = %s;
                """
                cursor.execute(query, (selected_pc, selected_ac))
            elif selected_pc:
                query = """
                    SELECT SUM("tdp2014") as "2014_tdp", SUM("ysrcp2014") as "2014_ycp", SUM("tdp_ycp_diff2014") as "2014_tdpmajority", SUM("tdp2019") as "2019_tdp", SUM("ysrcp2019") as "2019_ycp", SUM("tdp_ycp_diff2019") as "2019_tdp_majority"
                    FROM apt_20141019_polling_data_all_constituencies
                    WHERE pc_code = %s;
                """
                cursor.execute(query, (selected_pc, ))
            elif selected_ac:
                query = """
                    SELECT SUM("tdp2014") as "2014_tdp", SUM("ysrcp2014") as "2014_ycp", SUM("tdp_ycp_diff2014") as "2014_tdpmajority", SUM("tdp2019") as "2019_tdp", SUM("ysrcp2019") as "2019_ycp", SUM("tdp_ycp_diff2019") as "2019_tdp_majority"
                    FROM apt_20141019_polling_data_all_constituencies
                    WHERE ac_code = %s
                """
                cursor.execute(query, (selected_ac, ))

            polling_data = cursor.fetchall()

        return polling_data

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        if conn:
            conn.close()


# Placeholder function for updating age group pie chart
def update_age_group_chart(selected_pc_label, selected_ac_label, selected_pc, selected_ac, selected_mandal,
                           selected_polling_village):
    age_group_data = []
    if selected_pc and selected_ac and selected_mandal and selected_polling_village:
        age_group_data = get_age_group_data(selected_pc, selected_ac, selected_mandal, selected_polling_village)
    elif selected_pc and selected_ac and selected_mandal:
        age_group_data = get_age_group_data(selected_pc, selected_ac, selected_mandal, None)
    elif selected_pc and selected_ac:
        age_group_data = get_age_group_data(selected_pc, selected_ac, None, None)
    elif selected_ac:
        age_group_data = get_age_group_data(None, selected_ac, None, None)
    elif selected_pc:
        age_group_data = get_age_group_data(selected_pc, None, None, None)

    age_group_df = {
        'Age_Group': [row[0] for row in age_group_data],
        'NumVoters': [row[1] for row in age_group_data],
        'Color': get_age_group_colors([row[0] for row in age_group_data])  # Use a function to get caste-specific colors
    }
    age_group_fig = go.Figure()
    if age_group_data:
        age_group_fig.add_trace(go.Pie(labels=age_group_df['Age_Group'], values=age_group_df['NumVoters'],
                                       marker=dict(colors=age_group_df['Color']),
                                       textinfo='label+percent+value', showlegend=False))

        # Add annotation for total count
        # age_group_fig.update_layout(
        #    annotations=[
        #        dict(
        #            text="<b>2024 Age Group-Breakup:</b>",  # Title for the chart
        #            x=-0.18,
        #            y=1.4,  # Adjusted position of the title annotation
        #            showarrow=False,
        #            font=dict(family="Arial", size=14, color="black"),
        #        )
        #    ]
        # )
        age_group_fig.update_traces(hole=0.2)
        age_group_fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

    return age_group_fig


def get_age_group_data(selected_pc, selected_ac, selected_mandal, selected_polling_village):
    age_group_data = []
    try:
        conn = get_database_connection()
        selected_polling_village = selected_polling_village[0] if selected_polling_village else None
        selected_mandal = selected_mandal[0] if selected_mandal else None
        with conn.cursor() as cursor:
            # Modify the SQL query based on your database schema and filter conditions
            if selected_pc and selected_ac and selected_mandal and selected_polling_village:
                query = """
                    SELECT age_group, SUM(groupcount) 
                    FROM ap_agegroupcounts_jan24 
                    WHERE pc_number = %s AND assembly_number = %s AND mandal = %s AND village_or_area_name = %s AND age_group!='' GROUP BY age_group;
                """
                cursor.execute(query, (selected_pc, selected_ac, selected_mandal, selected_polling_village))
            elif selected_pc and selected_ac and selected_mandal:
                query = """
                    SELECT age_group, SUM(groupcount) 
                    FROM ap_agegroupcounts_jan24 
                    WHERE pc_number = %s AND assembly_number = %s AND mandal = %s AND age_group!='' GROUP BY age_group;
                """
                cursor.execute(query, (selected_pc, selected_ac, selected_mandal))
            elif selected_pc and selected_ac:
                query = """
                    SELECT age_group, SUM(groupcount) 
                    FROM ap_agegroupcounts_jan24 
                    WHERE pc_number = %s AND assembly_number = %s AND age_group!='' GROUP BY age_group;
                """
                cursor.execute(query, (selected_pc, selected_ac))
            elif selected_ac:
                query = """
                    SELECT age_group, SUM(groupcount) 
                    FROM ap_agegroupcounts_jan24 
                    WHERE assembly_number = %s AND age_group!='' GROUP BY age_group;
                """
                cursor.execute(query, (selected_ac,))
            elif selected_pc:
                query = """
                    SELECT age_group, SUM(groupcount)
                    FROM ap_agegroupcounts_jan24 
                    WHERE pc_number = %s AND age_group!='' GROUP BY age_group;
                """
                cursor.execute(query, (selected_pc,))

            age_group_data = cursor.fetchall()

        return age_group_data

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        if conn:
            conn.close()


# Callback to update the sub-caste bar chart based on filter selections
@dash_app1.callback(
    Output('sub-caste-polling-chart', 'figure'),
    [
        Input('polling-parliamentary-constituency-dropdown', 'value'),
        Input('polling-assembly-constituency-dropdown', 'value'),
        Input('polling-mandal-dropdown', 'value'),
        Input('polling-village-dropdown', 'value'),
        Input('polling-caste-dropdown', 'value'),
    ],
    [State('polling-parliamentary-constituency-dropdown', 'options'),
     State('polling-assembly-constituency-dropdown', 'options'),
     State('total-polling-voters', 'children')]
)
def update_polling_sub_caste_chart(selected_pc, selected_ac, selected_mandal, selected_polling_village,
                                   selected_polling_caste, pcoptions, acoptions, total_polling_voters):
    data1 = []
    title = ''
    voters_total_title = ''
    voters_caste_perc = ''
    total_voters_caste = ''
    estimated_2024_total = 0
    selected_pc_label = next((option['label'] for option in pcoptions if option['value'] == selected_pc), None)
    selected_ac_label = next((option['label'] for option in acoptions if option['value'] == selected_ac), None)

    if selected_pc and selected_ac and selected_mandal and selected_polling_village and selected_polling_caste:
        # Assuming get_polling_sub_caste_data returns a list of tuples (sub_caste, num_voters)
        data1 = get_polling_sub_caste_data(selected_pc, selected_ac, selected_mandal, selected_polling_village,
                                           selected_polling_caste)
        data1 = sorted(data1, key=lambda x: x[2], reverse=True)
        estimated_2024_total = getEstimated2024Count(selected_pc, selected_ac, selected_mandal,
                                                     selected_polling_village)
        mandal_str = ', '.join(map(str, selected_mandal)) if selected_mandal else ""
        village_str = ', '.join(map(str, selected_polling_village)) if selected_polling_village else ""
        voters_total_title = 'Village'
        if selected_polling_caste != 'casteall':
            caste_str = ', '.join(map(str, selected_polling_caste)) if selected_polling_caste else ""
            voters_caste_perc = caste_str
            total_voters_caste = caste_str
            title = f'<b>Sub-Caste Breakup PC:</b> <b style="color:red;">{selected_pc_label}</b>, <b>AC:</b> <b style="color:red;">{selected_ac_label}</b>, <b>Mandal:</b> <b style="color:red;">{mandal_str}</b>,' \
                    f' <b>Village:</b> <b style="color:red;">{village_str}</b>, <b>Caste:</b> <b style="color:red;">{caste_str}</b>'
        else:
            voters_caste_perc = 'All'
            total_voters_caste = 'All Caste'
            title = f'<b>Sub-Caste Breakup PC:</b> <b style="color:red;">{selected_pc_label}</b>, <b>AC:</b> <b style="color:red;">{selected_ac_label}</b>, <b>Mandal:</b> <b style="color:red;">{mandal_str}</b>,' \
                    f' <b>Village:</b> <b style="color:red;">{village_str}</b>, <b>Caste:</b> <b style="color:red;">All</b>'
    elif selected_pc and selected_ac and selected_mandal and selected_polling_caste:
        # Assuming get_polling_sub_caste_data returns a list of tuples (sub_caste, num_voters)
        data1 = get_polling_sub_caste_data(selected_pc, selected_ac, selected_mandal, None, selected_polling_caste)
        data1 = sorted(data1, key=lambda x: x[2], reverse=True)
        estimated_2024_total = getEstimated2024Count(selected_pc, selected_ac, selected_mandal, None)
        mandal_str = ', '.join(map(str, selected_mandal)) if selected_mandal else ""
        voters_total_title = 'Mandal';
        if selected_polling_caste != 'casteall':
            caste_str = ', '.join(map(str, selected_polling_caste)) if selected_polling_caste else ""
            voters_caste_perc = caste_str
            total_voters_caste = caste_str
            title = f'<b>Sub-Caste Breakup PC:</b> <b style="color:red;">{selected_pc_label}</b>, <b>AC:</b> <b style="color:red;">{selected_ac_label}</b>, <b>Mandal:</b> <b style="color:red;">{mandal_str}</b>,' \
                    f' <b>Caste:</b> <b style="color:red;">{caste_str}</b>'
        else:
            voters_caste_perc = 'All'
            total_voters_caste = 'All Caste'
            title = f'<b>Sub-Caste Breakup PC:</b> <b style="color:red;">{selected_pc_label}</b>, <b>AC:</b> <b style="color:red;">{selected_ac_label}</b>, <b>Mandal:</b> <b style="color:red;">{mandal_str}</b>,' \
                    f' <b>Caste:</b> <b style="color:red;">All</b>'
    elif selected_pc and selected_ac and selected_polling_caste:
        # Assuming get_polling_sub_caste_data returns a list of tuples (sub_caste, num_voters)
        data1 = get_polling_sub_caste_data(selected_pc, selected_ac, None, None, selected_polling_caste)
        data1 = sorted(data1, key=lambda x: x[2], reverse=True)
        estimated_2024_total = getEstimated2024Count(selected_pc, selected_ac, None, None)
        voters_total_title = 'AC';
        if selected_polling_caste != 'casteall':
            caste_str = ', '.join(map(str, selected_polling_caste)) if selected_polling_caste else ""
            voters_caste_perc = caste_str
            total_voters_caste = caste_str
            title = f'<b>Sub-Caste Breakup PC:</b> <b style="color:red;">{selected_pc_label}</b>, <b>AC:</b> <b style="color:red;">{selected_ac_label}</b>,' \
                    f' <b>Caste:</b> <b style="color:red;">{caste_str}</b>'
        else:
            voters_caste_perc = 'All'
            total_voters_caste = 'All Caste'
            title = f'<b>Sub-Caste Breakup PC:</b> <b style="color:red;">{selected_pc_label}</b>, <b>AC:</b> <b style="color:red;">{selected_ac_label}</b>,' \
                    f' <b>Caste:</b> <b style="color:red;">All</b>'
    elif selected_pc and selected_polling_caste:
        # Assuming get_polling_sub_caste_data returns a list of tuples (sub_caste, num_voters)
        data1 = get_polling_sub_caste_data(selected_pc, None, None, None, selected_polling_caste)
        data1 = sorted(data1, key=lambda x: x[2], reverse=True)
        estimated_2024_total = getEstimated2024Count(selected_pc, None, None, None)
        voters_total_title = 'PC';
        if selected_polling_caste != 'casteall':
            caste_str = ', '.join(map(str, selected_polling_caste)) if selected_polling_caste else ""
            voters_caste_perc = caste_str
            total_voters_caste = caste_str
            title = f'<b>Sub-Caste Breakup PC:</b> <b style="color:red;">{selected_pc_label}</b>, <b>Caste:</b> <b style="color:red;">{caste_str}</b>'
        else:
            voters_caste_perc = 'All'
            total_voters_caste = 'All Caste'
            title = f'<b>Sub-Caste Breakup PC:</b> <b style="color:red;">{selected_pc_label}</b>, <b>Caste:</b> <b style="color:red;">All</b>'
    elif selected_ac and selected_polling_caste:
        # Assuming get_polling_sub_caste_data returns a list of tuples (sub_caste, num_voters)
        data1 = get_polling_sub_caste_data(None, selected_ac, None, None, selected_polling_caste)
        data1 = sorted(data1, key=lambda x: x[2], reverse=True)
        estimated_2024_total = getEstimated2024Count(None, selected_ac, None, None)
        voters_total_title = 'AC'
        if selected_polling_caste != 'casteall':
            caste_str = ', '.join(map(str, selected_polling_caste)) if selected_polling_caste else ""
            voters_caste_perc = caste_str
            total_voters_caste = caste_str
            title = f'<b>Sub-Caste Breakup AC:</b> <b style="color:red;">{selected_ac}</b>, <b>Caste:</b> <b style="color:red;">{caste_str}</b>'
        else:
            # voters_caste_perc = 'All'
            total_voters_caste = 'All Caste'
            title = f'<b>Sub-Caste Breakup AC:</b> <b style="color:red;">{selected_ac}</b>, <b>Caste:</b> <b style="color:red;">All</b>'

    df = pd.DataFrame(data1, columns=['Caste', 'Sub-Caste', 'NumVoters'])
    if total_polling_voters:
        total_voters_float = float(total_polling_voters)
    else:
        total_voters_float = 0
    # Calculate percentages and convert to strings with two digits after the decimal point
    df['Percentage'] = (df['NumVoters'] / df['NumVoters'].sum() * 100).apply(lambda x: '{:.2f}%'.format(x))
    df['TotalPercentage'] = (df['NumVoters'].astype(float) / total_voters_float * 100).apply(
        lambda x: '{:.2f}%'.format(x))
    df['TotalPercentage'] = df['TotalPercentage'].astype(str).str.replace('%', '')
    df['TotalPercentage'] = df['TotalPercentage'].astype(float)
    df['2024 Estimated'] = (estimated_2024_total / 100) * df['TotalPercentage']
    df['2024 Estimated'] = df['2024 Estimated'].astype(int).apply(lambda x: '{:d}'.format(x))
    # Calculate total number of voters and format it to include in the table
    total_voters_str = f'<b>Total {total_voters_caste}: {df["NumVoters"].sum()}</b>'
    total_ap_voters_str = f'<b>{voters_total_title} Voters: {total_polling_voters}</b>'
    # voters_caste_perc = f'<b>{voters_caste_perc}: Caste</b>'
    estimated_total = f'<b>Total Estimated 2024: {estimated_2024_total}</b>'

    # Create a new row to display the totals
    total_row = pd.DataFrame({'Sub Caste': [''],
                              'Caste': [''],
                              'NumVoters': [total_voters_str],
                              'TotalPercentage': [total_ap_voters_str],
                              '2024 Estimated': [estimated_total],  # Add a column for estimated total in 2024
                              })

    # Concatenate the total row with the original DataFrame
    df = pd.concat([total_row, df]).reset_index(drop=True)

    # Remove null values from other columns
    df.fillna('', inplace=True)

    sub_caste_fig = go.Figure(data=[go.Table(
        header=dict(values=['Sub Caste', 'Caste', '2019 Num of Voters', 'Percentage of', '2024 Estimated', 'Comments'],
                    align=['left', 'center', 'center'],
                    font=dict(size=14),
                    height=30,
                    fill=dict(color='lightgray'),
                    line=dict(color='darkslategray', width=2)),
        cells=dict(values=[df['Sub-Caste'], df['Caste'], df['NumVoters'].astype(str), df['TotalPercentage'],
                           df['2024 Estimated'], ''],
                   align=['left', 'center', 'center'],
                   font=dict(size=14),
                   height=20,
                   fill=dict(color='white'),
                   line=dict(color='darkslategray', width=1)),
    )])
    # Add <colgroup> and <col> elements to adjust column widths
    sub_caste_fig.update_layout(
        title=title,
        margin=dict(b=80, t=60, l=40, r=40),
        font=dict(family="Arial", size=14, color="RebeccaPurple"),
        title_font=dict(family="Arial", size=12, color="black"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        # Increase space between rows
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
    )
    # Set the column widths
    column_widths = [0.1, 0.03, 0.05, 0.05, 0.04, 0.2]  # Adjust as needed

    # Apply the column widths
    sub_caste_fig.update_layout(
        autosize=True,
        template="plotly_white",  # Apply Plotly's white template
        font=dict(family="Arial"),  # Adjust font family
        title_font=dict(size=14),  # Adjust title font size
        margin=dict(l=20, r=65, t=45, b=20),  # Adjust margins
    )

    # Update the table layout with the column widths
    sub_caste_fig.update_traces(columnwidth=column_widths)
    return sub_caste_fig


def getEstimated2024Count(selected_pc, selected_ac, selected_mandal, selected_polling_village):
    conn = None
    cursor = None
    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        query = """
            SELECT SUM(groupcount) 
            FROM ap_agegroupcounts_jan24 
            WHERE 1=1
        """

        params = []

        if selected_pc:
            query += " AND pc_number = %s"
            params.append(selected_pc)
        if selected_ac:
            query += " AND assembly_number = %s"
            params.append(selected_ac)
        if selected_mandal:
            selected_mandal = selected_mandal[0] if selected_mandal else None
            query += " AND mandal = %s"
            params.append(selected_mandal)
        if selected_polling_village:
            selected_polling_village = selected_polling_village[0] if selected_polling_village else None
            query += " AND village_or_area_name = %s"
            params.append(selected_polling_village)

        cursor.execute(query, params)

        # Fetch the result
        total_estimated_count = cursor.fetchone()[0]
        return total_estimated_count
    except Exception as e:
        print("Error:", e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_polling_sub_caste_data(selected_pc, selected_ac, selected_mandal, selected_polling_village,
                               selected_polling_caste):
    conn = None
    cursor = None

    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        query = """
            SELECT caste, subcaste, SUM(grand_total) 
            FROM BLI 
            WHERE caste not in ('Dead', 'Deleted', 'Not Traced')
        """

        params = []

        if selected_pc:
            query += " AND pc_code = %s"
            params.append(selected_pc)
        if selected_ac:
            query += " AND ac_no = %s"
            params.append(selected_ac)
        if selected_mandal:
            selected_mandal = selected_mandal[0] if selected_mandal else None
            query += " AND mandal_name = %s"
            params.append(selected_mandal)
        if selected_polling_village:
            selected_polling_village = selected_polling_village[0] if selected_polling_village else None
            query += " AND village_name = %s"
            params.append(selected_polling_village)
        if selected_polling_caste != 'casteall':
            selected_polling_caste = selected_polling_caste[0] if selected_polling_caste else None
            query += " AND caste = %s"
            params.append(selected_polling_caste)

        # Group by subcaste and execute the query
        query += " GROUP BY caste, subcaste;"
        cursor.execute(query, params)

        # Fetch all the results
        sub_caste_data = cursor.fetchall()

        # Return the fetched data
        return sub_caste_data

    finally:
        # Close the cursor and connection in the final block to ensure they are always closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_age_group_colors(age_group_list):
    # Assign colors based on age_group
    age_group_colors = {
        '18-25': 'skyblue',
        '26-40': 'salmon',
        '41-60': 'lightgreen',
        '61-85': 'orchid',
        'above85': 'gray'
    }
    # Map each caste to its corresponding color, default to 'black' if not found
    return [age_group_colors.get(age_group, 'black') for age_group in age_group_list]


# Define functions to generate figures from data
def generate_pie_chart(data):
    # Process data for the pie chart
    df = {
        'Caste': [],
        'NumVoters': [],
        'Color': []
    }

    # Create the pie chart
    pie_chart_figure = go.Figure()

    if data:
        # Add pie chart trace
        pie_chart_figure.add_trace(go.Pie(labels=df['Caste'], values=df['NumVoters'], marker=dict(colors=df['Color']),
                                          textinfo='label+percent+value'))

        # Calculate total count
        total_count = sum(df['NumVoters'])

        # Add annotation for total count
        pie_chart_figure.update_layout(
            annotations=[
                dict(
                    text=f'Total Voters: {total_count}',
                    x=0.5,
                    y=1.1,  # Adjust the position as needed
                    showarrow=False,
                    font=dict(family="Arial", size=14, color="RebeccaPurple"),
                )
            ],
            title=dict(
                font=dict(family="Arial", size=14, color="black")
            )
        )
        pie_chart_figure.update_traces(hole=0.3)

    return pie_chart_figure


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
