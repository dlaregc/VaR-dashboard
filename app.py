from dash import Dash, dcc, html, Input, Output, ctx, State, no_update, dash_table
import var as var
import datetime as dt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

app = Dash(__name__)

app.layout = html.Div(
    className = "background",
    children = [
        html.H1(
            children = "VaR and CVaR",
            className = "title"),
        html.P(
            children = "Analyse the VaR and CVaR of various portfolios with either Historical, Monte Carlo or Parametric simulations!",
            className = "intro"),
        html.Div(
            className = "input-container",
            children = [
                html.Div(
                    children = [
                        html.Label(
                            children = "Ticker:",
                            className = "button-label"
                        ),
                        dcc.Input(
                            id = "ticker-input",
                            value = "Ticker",
                            className = "input",
                            type = "text",
                        ),
                    ]
                ),
                html.Div(
                    children = html.Button(
                        children = "Add Ticker",
                        id = "add-ticker-button",
                        className = "add-button",
                        n_clicks = 0
                    )
                ),
                html.Div(
                    children = [
                        html.Label(
                            children = "Days back:",
                            className = "button-label"
                        ),
                        dcc.Input(
                            id = "days-input",
                            value = 1,
                            className = "input",
                            type = "number",
                        )
                    ]
                ),
                html.Div(
                    children = [
                        html.Label (
                            children = "Alpha:",
                            className = "button-label"
                        ),
                        dcc.Input(
                            id = "alpha",
                            value = 5,
                            className = "input",
                            type = "number",
                        ),
                    ]
                )
            ],
        ),
        html.Div(
            className = "table-container",
            children = [
                dash_table.DataTable(
                    id = "ticker-table",
                    data = [],
                    columns = [{"id": "tick", "name": "Ticker"},],
                    page_size = 5,
                    row_deletable = True,
                    style_header = {
                        "backgroundColor": "#403938",
                        "color": "ghostwhite",
                    },
                    style_data = {
                        "backgroundColor": "#322C2B",
                        "color": "ghostwhite",
                    }
                )
            ],
        ),
        html.P( 
            id = "ticker-input-chosen",
            className = "simulation-chosen"
        ),
        html.Div(
            children = [
                html.Button(
                    children = "Historical", 
                    className = "button",
                    id = "historical",
                    ),
                # html.Button( # configure next time
                #     children = "Parametric",
                #     className = "button",
                #     id = "parametric",
                #     ),
                # html.Button(
                #     children = "Monte Carlo",
                #     className = "button",
                #     id = "monte-carlo",
                #     ),
            ],
            id = "simluation",
            className = "button-container",
        ),
        html.P(
            id = "chosen-simulation",
            className = "simulation-chosen"
        ),
        html.Div(
            className = "graph-container",
            children = dcc.Graph(id = "subplot-1",),
        ),
        html.Div(
            className = "explanation-container",
            children = [
                html.Div(
                    children = [
                        html.H2(
                            children = "Value at Risk",
                            className = "cvar-title"
                        ),
                        html.Div(),
                        html.P(
                            id = "var",
                            className = "var-explanation",
                        )
                    ],
                ),
                html.Div(
                    children = [
                        html.H2(
                            children = "Conditional Value at Risk",
                            className = "var-title"
                        ),
                        html.Div(),
                        html.P(
                            id = "cvar",
                            className = "cvar-explanation",
                        )
                    ],
                )
            ]
        )
    ]
)

# add ticker to ticker_table for multi asset
@app.callback(
        Output("ticker-table", "data"),
        State("ticker-input", "value"),
        Input("add-ticker-button", "n_clicks"),
        State("ticker-table", "data"),
)

def add_data_to_ticker_table(ticker, add_ticker, rows):
    if "add-ticker-button" == ctx.triggered_id:
        ticker_list = list(map(lambda x: x["tick"], rows))
        if var.check_ticker_exists(ticker) and ticker not in ticker_list:
            rows.append({"tick": ticker})
    return rows

# updating graphs based off table
@app.callback(
        Output("ticker-input-chosen", "children"),
        Output("subplot-1", "figure"),
        Output("var", "children"),
        Output("cvar", "children"),
        Input("historical", "n_clicks"),
        State("days-input", "value"),
        State("alpha", "value"),
        State("ticker-table", "data")
)

def graph_update(n_clicks, days_back, alpha, table):

    var_msg = "The Value at Risk (VaR) is _% of the portfolio value at a _% confidence interval"
    cvar_msg = "The Conditional Value at Risk (VaR) is _% of the portfolio value at a _% confidence interval"
    fig_1 = make_subplots()
    fig_1.update_layout(
            autosize = True,
            width = 1300,
            height = 500,
            showlegend = False,
            paper_bgcolor = "#322C2B",
            plot_bgcolor = "#322C2B",
            font = {
                "color": "ghostwhite",
                "family": "monospace",
            }
        )

    if n_clicks == 0 or len(table) == 0:
        return "Choose a ticker to simulate", fig_1, var_msg, cvar_msg
    elif days_back <= 1:
        return "Days must take the range [2, infinity)", no_update, no_update, no_update
    elif alpha > 100 or alpha <= 0:
        return "Alpha must be take the range (0, 100]", no_update, no_update, no_update
    elif "historical" != ctx.triggered_id:
        return "Choose a simulation type", no_update, no_update, no_update
    
    ticker_arr = list(map(lambda x: x["tick"], table))
    ticker_input = " ".join(ticker_arr)

    try:
        stock_data, returns, mean_returns, start, end = var.data(ticker_input, days_back)
    except Exception as e:
        err = e
        return err.args, no_update, no_update, no_update
    else:
        returns_msg = f"Adjusted Closing Price of {ticker_arr[0]} from {start} to {end}"
        dist_msg = f"Distribution of Returns for {ticker_arr[0]}"
        msg = f"{ticker_arr[0]} successfully simulated"

        if len(ticker_arr) > 1:
            returns_msg = f"Value of Portfolio from {start} to {end}"
            dist_msg = f"Distribution of Returns for Portfolio"
            msg = "Portfolio successfully simulated"

        dist = var.distribution_of_returns(returns)

        fig_1 = make_subplots(          
            rows = 1, cols = 2,
            subplot_titles = (
                returns_msg,
                dist_msg,
            )
        )
        fig_1.add_trace(
            go.Scatter(
                x = stock_data["Date"],
                y = stock_data["Adj Close"],
                line = {
                    "color": "#78b18c",
                },
            ),
            row = 1,
            col = 1,
        )
        fig_1.add_trace(
            go.Scatter(           
                x = dist["bins"],
                y = dist["count"],
                line = {
                    "color": "#76a4d8",
                },
                mode = "lines",
                line_shape = "spline",
            ),
            row = 1,
            col = 2,
        )
        fig_1.add_shape(
            type = "line",
            xref = "x",
            yref = "paper",
            x0 = mean_returns,
            y0 = 0,
            x1 = mean_returns,
            y1 = max(dist["count"].tolist()),
            line = {
                "dash": "dash",
                "color": "#e46969",
                "width": 2,
            },
            row = 1,
            col = 2,
        )
        fig_1.update_layout(
            autosize = True,
            width = 1200,
            height = 500,
            showlegend = False,
            paper_bgcolor = "#322C2B",
            plot_bgcolor = "#322C2B",
            font = {
                "color": "ghostwhite",
                "family": "monospace",
            }
        )

        # var output
        VaR = var.var(returns, alpha = alpha)
        CVaR = var.cvar(returns, VaR)
        var_msg = f"The Value at Risk (VaR) is {VaR}% of the portfolio value at a {alpha}% confidence interval"
        cvar_msg = f"The Conditional Value at Risk (VaR) is {CVaR}% of the portfolio value at a {alpha}% confidence interval"
        return msg, fig_1, var_msg, cvar_msg

# updating simulation chosen
@app.callback(
    Output("chosen-simulation", "children"),
    Input("historical", "n_clicks"),
    # Input("parametric", "n_clicks"),
    # Input("monte-carlo", "n_clicks")
)

def update_simulation_chosen(historical): # add "parametric" and "monte-carlo" as parameters after solving problem
    msg = "A simulation has not been chosen yet"
    if "historical" == ctx.triggered_id:
        msg = "Historical Simulation"
    # elif "parametric" == ctx.triggered_id:
    #     msg = "Paramteric Simulation"
    # elif "monte-carlo" == ctx.triggered_id:
    #     msg = "Monte Carlo Simulation"
    return msg

if __name__ == "__main__":
    app.run_server(debug = True)