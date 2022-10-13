from dash import html, dcc, Dash
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import os

def create_dash_app(flask_app):
    external_scripts = [{
        'src': 'https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js',
    }]
    dash_app = Dash(server=flask_app,name="Dashboard",url_base_pathname="/dash/", external_scripts = external_scripts)
    dash_app.title = "Graphs - DNAScanner"
   

    dash_app.layout = html.Div([
           dcc.Location(id='url', refresh=False),
           dcc.Store(id="url-value"),
           dcc.Store(id="inc-conc"),
           dcc.Dropdown(id="sequence-selector",
           placeholder="Select Sequence",
           ),
           html.Br(),
           dcc.Dropdown(id="graph-type",
           placeholder="Select Graph Type",
           ),
           html.Br(),
           dcc.Dropdown(id="graph-y",
           placeholder="Select Y-Axis",
           ),
           html.P("Please clear the options before changing graph-type"),
           html.Br(),
           dcc.Graph(
            id = 'graph-figure',
            figure = {}
            ), 
    ])

    @dash_app.callback([Output('url-value', 'data'),
    Output('inc-conc', 'data')],
              Input('url', 'pathname'))
    def return_folder(pathname):
        return pathname.split('/')[2],pathname.split("/")[3]

    @dash_app.callback([
    Output(component_id="sequence-selector",component_property="options"),
    Output(component_id="graph-type",component_property="options"),
    Output(component_id="graph-y",component_property="options"),
    Output(component_id="graph-figure",component_property="figure"),
    Output(component_id="sequence-selector",component_property="value"),
    ],
    [Input(component_id="url-value",component_property="data"),
    Input(component_id="inc-conc",component_property="data"),
    Input(component_id="graph-type",component_property="value"),
    Input(component_id="sequence-selector",component_property="value"),
    Input(component_id="graph-y",component_property="value")
    ])
    def dropdown_update(folder,inc_conc,graph_type,sequence,graph_y):
        print(x[6:].split("%")[0] for x in os.listdir("static/Output/" + folder + "/Parameters/")[:-1])
        sequences = [x[6:].split("%")[0] for x in os.listdir("static/Output/" + folder + "/Parameters/")[:-1]]
        if inc_conc == "on":
            graph_types = ["Dinucleotide Concentration","Trinucleotide Concentration","Dinucleotide Parameters","Trinucleotide Parameters"]
        else:
            graph_types = ["Dinucleotide Parameters","Trinucleotide Parameters"]
        df = ""
        fig = ""
        dropdown_list = ""
        if graph_type == "Dinucleotide Concentration":
            df = "static/Output/" + folder + "/Nucleotide_Concentration/DNAScanner_DiNucleotideRule__Output.csv"
            x = 3
            plot_type = "Concentration"
        elif graph_type == "Trinucleotide Concentration":
            df = "static/Output/" + folder + "/Nucleotide_Concentration/DNAScanner_TriNucleotideRule__Output.csv"
            x = 3
            plot_type = "Concentration"
        elif graph_type == "Dinucleotide Parameters":
            df = "static/Output/" + folder + "/Parameters/Param%" + sequence + "%DiNucleotide.csv"
            x = 2
            plot_type = "Parameter"
        elif graph_type == "Trinucleotide Parameters":
            df = "static/Output/" + folder + "/Parameters/Param%" + sequence + "%TriNucleotide.csv"
            x = 2
            plot_type = "Parameter"
        if df != "":
            df = pd.read_csv(df)
            dropdown_list = df.columns.values.tolist()[x:]
            spl = []
            for sp in range(len(df.index)):
                spl.append(int(sp + 1))   
            fig = px.line(df, x=spl, y=graph_y)
            fig.update_xaxes(rangeslider_visible=True) 
            fig.update_layout(title=f"{graph_y} {plot_type} Plot",xaxis_title="Position",yaxis_title=f"{graph_y} Block Score")         
        return sequences, graph_types, dropdown_list, fig, sequences[0]


    return dash_app

