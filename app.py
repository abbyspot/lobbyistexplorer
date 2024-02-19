import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc

raw_df = pd.read_csv('ALL_BYCLIENT_DATA_20202024.csv')
df = raw_df[["client", "lobbyist", "start", "stop", "amount"]]
lobbyists_list = list(df['lobbyist'].unique())
clients_list = list(df['client'].unique())


def search_df(q):
    if q=="": return df

    results = df[df.lobbyist.str.contains(q.title())]
    # print(results)
    return results.to_dict('records')

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

def lobbyist_search_card():
    return dbc.Card([
        html.H5("Search lobbyist:"),
        dbc.Input(
            id='lobbyist-input',
            placeholder="Search lobbyist...",
            type="text"
        )
    ])

def client_selection_card():
    return dbc.Card([
        html.H5("Select Client:"),
        dcc.Dropdown(
            clients_list,
            id="client-dropdown",
            value=[],
            multi=True,
            placeholder="Filter by clients..."
        )
    ])

def filter_df(lobbyist_search, client_search):
    if (not lobbyist_search) and (not client_search): filtered_df = df
    else:
        if not lobbyist_search: lobbyist_search = ""
        if not client_search: filtered_df = df[df['lobbyist'].str.contains(lobbyist_search.title())]
        else: filtered_df = df[(df['lobbyist'].str.contains(lobbyist_search.title()) & df['client'].isin(client_search))]
    return filtered_df

def generate_datatable(lobbyist_search, client_search):
    filtered_df = filter_df(lobbyist_search, client_search)
    
    return dash_table.DataTable(
        filtered_df.to_dict('records'),
        [{"name": i, "id": i} for i in filtered_df.columns],
        id='output-datatable',
        page_size=20
    )

def generate_profile_panel(lobbyist_name):
    filtered_df = raw_df[raw_df['lobbyist'] == lobbyist_name]
    first_row = filtered_df.iloc[0]
    
    list_of_clients = [
        html.Div([f"Client: {row.client}\nDuration: {row.start}—{row.stop}\n\n"])
        for i, row in filtered_df.iterrows()
    ]

    output_text=html.Div([
        html.H3(first_row.lobbyist),
        html.Br(),
        f"Phone #: {first_row.phone_number}",
        html.Br(),
        f"Address: {first_row.lobby_street_address} {first_row.city}, {first_row.state} {first_row.zip}",
        html.Br(),
        f"Filer ID: {first_row.filer_id}",
        html.Br(),
        html.Br(),
        html.Br(),
        *list_of_clients
    ])
    # output_text = str(filtered_df.iloc[0].to_dict())
    return dbc.Card([
        output_text
    ])

def layout():
    return html.Div([
        dbc.Row([
            dbc.Col(html.Div(lobbyist_search_card())),
            dbc.Col(html.Div(client_selection_card())),
        ]),
        dbc.Row([
            dbc.Col(html.Div(
                id='output-table'
            ))
        ]),
        dbc.Row([
            dbc.Col(html.Div(
                id='lobbyist-profile-panel'
            ))
        ])
        # dbc.Row([
        #     dbc.Col(search_card()),
        #     dbc.Col(dbc.Card("Sack"))
        # ])
])


app.layout = layout()

@callback(
    Output("output-table", "children"),
    Input("lobbyist-input", "value"),
    Input("client-dropdown", "value"),
)
def update_datatable(lobbyist_input_value, client_dropdown_value):
    return [generate_datatable(lobbyist_input_value, client_dropdown_value)]
# def update_output(search_input):
#     return search_df(search_input)

@callback(
    Output('lobbyist-profile-panel', 'children'),
    Input('output-datatable', 'active_cell'),
    Input("lobbyist-input", "value"),
    Input("client-dropdown", "value"),
)
def update_profile_panel(active_cell, lobbyist_input_value, client_dropdown_value):
    if not active_cell: return [dbc.Panel("SELECT CELL TO VIEW LOBBYIST PROFILE")]
    active_row = active_cell['row']
    live_df = filter_df(lobbyist_input_value, client_dropdown_value)
    lobbyist_name = live_df.iloc[active_row,].lobbyist
    return [generate_profile_panel(lobbyist_name)]

server = app.server

if __name__ == '__main__':
    app.run(debug=False)
