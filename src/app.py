#!/usr/bin/env python3
# 1. Import Dash
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
# import dash_html_components as html

import pandas as pd
import plotly.express as px

# --- DAHSBOARD ELEMENTS ---

# DATASET
gpp = pd.read_csv('data_input/power_plant.csv')
c = dict(zip(gpp["primary_fuel"].unique(), px.colors.qualitative.G10))

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
    ],
    brand="Global Power Plant",
    brand_href="#",
    color="#696969",
    dark=True,
    sticky='top'
)

# CARDS

total_country = [
    dbc.CardHeader('Number of Country', class_name="text-center"),
    dbc.CardBody(
        [
            html.H1(gpp['country_long'].unique().shape[0])
        ]
    )
]

total_power_plant = [
    dbc.CardHeader('Total Power Plant'),
    dbc.CardBody(
        [
            html.H1(gpp['name of powerplant'].unique().shape[0])
        ]
    )
]

fuel_type = [
    dbc.CardHeader('Total Type of Fuel'),
    dbc.CardBody(
        [
            html.H1(gpp['primary_fuel'].unique().shape[0])
        ]
    )
]


# GRAPH

###### --- CHOROPLETH
agg1 = pd.crosstab(
    index=[gpp['country code'], gpp['start_year']],
    columns='No of Power Plant'
).reset_index()

map = px.choropleth(agg1.sort_values("start_year"),
                    locations='country code',
                    color_continuous_scale='tealgrn',
                    color='No of Power Plant',
                    animation_frame='start_year',
                    template='ggplot2')

# 2. Create a Dash app instance
app = dash.Dash(
    name='Global Power Plant',
    external_stylesheets=[dbc.themes.CYBORG]
)
app.title = 'Global Power Plant Dashboard'

server = app.server

# --- DASHBOARD LAYOUT

app.layout = html.Div(children=[
    navbar,
    html.Br(),

    # Main page
    html.Div(
        [
            # ----- ROW 1
            dbc.Row(
                [
                    # --- COLUMN 1
                    dbc.Col(
                        [
                            dbc.Card(
                                # , style={"width": "500px", "height": "200px"}
                                total_country, color='aquamarine'

                            ),
                            html.Br(),
                            dbc.Card(
                                total_power_plant, color='plum',
                            ),
                            html.Br(),
                            dbc.Card(
                                fuel_type, color='lightsalmon',
                            ),
                        ],
                        width=3,
                    ),

                    # --- COLUMN 2
                    dbc.Col(
                        [
                            dcc.Graph(
                                id='choropleth',
                                figure=map
                            )
                        ],
                        width=9
                    ),
                ]
            ),

            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                # , style={"width": "500px", "height": "200px"}
                                total_country, color='aquamarine', className="text-center"

                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                total_power_plant, color='plum', class_name="text-center"
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                fuel_type, color='lightsalmon', class_name="text-center"
                            ),
                        ]
                    ),




                ]
            ),
            # ----- ROW 2
            dbc.Row(
                [
                    # --- COLUMN 1
                    dbc.Col(
                        [
                            html.H1(
                                'Analysis by Country',
                            ),
                            dbc.Tabs(
                                [
                                    dbc.Tab(
                                        dcc.Graph(
                                            id='plot1_overall',
                                        ),
                                        label='Ranking',
                                    ),
                                    dbc.Tab(
                                        dcc.Graph(
                                            id='plot3_capacity',
                                        ),
                                        label='Distribution'
                                    ),
                                ]
                            ),
                        ],
                        width=8,
                    ),

                    # --- COLUMN 2
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader('Select Country'),
                                    dbc.CardBody(
                                        dcc.Dropdown(
                                            id='list_country',
                                            options=gpp['country_long'].unique(
                                            ),
                                            value='Indonesia',
                                        ),
                                    ),
                                ]
                            ),
                            dcc.Graph(
                                id='plot2_fuel',
                            ),
                        ],
                        width=4,
                    ),

                ]
            ),

        ],
        style={
            'padding-right': '30px',
            'padding-left': '30px'
        }
    )


],
    style={
    'backgroundColor': 'seashell',
},
)

# ---- CALLBACK TO SELECT COUNTRY

# ---- PLOT 1: Barplot


@app.callback(
    Output(component_id='plot1_overall', component_property='figure'),
    Input(component_id='list_country', component_property='value'),
)
def update_plot1(country_name):
    # --- BAR CHART
    # Data aggregation
    gpp_indo = gpp[gpp['country_long'] == country_name]
    top_indo = gpp_indo.sort_values('capacity in MW').tail(10)

    # Visualize
    plot1_bar = px.bar(
        top_indo,
        x='capacity in MW',
        y='name of powerplant',
        template='ggplot2',
        title=f'Rangking of Overall Power Plants in {str(country_name)}'
    )
    plot1_bar.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
    })
    return plot1_bar

# ---- PLOT 2: Pie Chart


@app.callback(
    Output(component_id='plot2_fuel', component_property='figure'),
    Input(component_id='list_country', component_property='value'),
)
def update_plot2(country_name):
    # --- PIE CHART
    # aggregation
    gpp_indo = gpp[gpp['country_long'] == country_name]
    agg2 = pd.crosstab(
        index=gpp_indo['primary_fuel'],
        columns='No of Power Plant'
    ).reset_index()

    # visualize
    plot2_pie = px.pie(
        agg2,
        values='No of Power Plant',
        names='primary_fuel',
        color='primary_fuel',
        # color_discrete_sequence=['aquamarine',
        #                          'salmon', 'plum', 'grey', 'slateblue'],
        color_discrete_map=c,
        template='ggplot2',
        hole=0.4,
        labels={
            'primary_fuel': 'Type of Fuel'
        }
    )
    return plot2_pie

# ---- PLOT 3: Box Plot


@app.callback(
    Output(component_id='plot3_capacity', component_property='figure'),
    Input(component_id='list_country', component_property='value'),
)
def update_plot2(country_name):
    gpp_indo = gpp[gpp['country_long'] == country_name]
    ###### --- BOXPLOT
    gpp_capacity = gpp_indo[gpp_indo['capacity in MW'] < 3000]
    plot3_box = px.box(
        gpp_capacity,
        color='primary_fuel',
        color_discrete_map=c,
        y='capacity in MW',
        template='ggplot2',
        title=f'Distribution of capacity in MW in each fuel in {str(country_name)}',
        labels={
            'primary_fuel': 'Type of Fuel'
        }
    )
    return plot3_box


# 3. Start the Dash server
if __name__ == "__main__":
    app.run(debug=True)
