from plotly.data import gapminder
from dash import dcc, html, Dash, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# External CSS (Bootstrap)
css = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css"]
app = Dash(name="Gapminder Dashboard", external_stylesheets=css)

################### DATASET ####################################
# 使用 gapminder()（注意：你原先使用了 gapminder(datetimes=True, centroids=True, pretty_names=True)）
# 保持兼容性：为确保 datetimes 可用，按你的环境选择相应调用；这里示例使用基本 gapminder()
gapminder_df = gapminder()
# 标准化列名（根据你原数据的列名）
# 如果你的 gapminder 返回的是其他列名，请调整下面的列名映射
gapminder_df = gapminder_df.rename(columns={
    "gdpPercap": "GDP per Capita",
    "lifeExp": "Life Expectancy",
    "pop": "Population",
    "continent": "Continent",
    "country": "Country",
    "year": "Year",
    "iso_alpha": "ISO Alpha Country Code"
}, errors="ignore")

# 如果 Year 是数值，确保为 int
if pd.api.types.is_datetime64_any_dtype(gapminder_df.get("Year")):
    gapminder_df["Year"] = gapminder_df["Year"].dt.year
gapminder_df["Year"] = gapminder_df["Year"].astype(int)

#################### STYLING / COLOR PALETTES ##################
# 统一样式：使用 plotly_white 模板 + 柔和色板
DEFAULT_TEMPLATE = "plotly_white"
CATEGORY_COLORS = px.colors.qualitative.Pastel  # 柔和类别色板
CONTINUOUS_MAP = "Viridis"  # 连续色标（choropleth）

COMMON_LAYOUT_KWARGS = dict(
    template=DEFAULT_TEMPLATE,
    font=dict(family="Inter, Arial, sans-serif", size=12),
)

#################### CHARTS #####################################
def create_table():
    # 使用 go.Table 并美化表头与交替行色
    header_fill = "#0d6efd"  # bootstrap primary
    header_font_color = "white"
    cell_fill1 = "#ffffff"
    cell_fill2 = "#f6f8fb"

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(gapminder_df.columns),
                    fill_color=header_fill,
                    font=dict(color=header_font_color, size=13),
                    align='left'),
        cells=dict(values=[gapminder_df[col] for col in gapminder_df.columns],
                   fill_color=[ [cell_fill1, cell_fill2] * (len(gapminder_df)//2 + 1) ],
                   align='left',
                   font=dict(color="#222222", size=11))
    )])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin={"t":10, "l":0, "r":0, "b":0}, height=700, **COMMON_LAYOUT_KWARGS)
    return fig

def create_population_chart(continent="Asia", year=1952):
    filtered_df = gapminder_df[(gapminder_df.Continent==continent) & (gapminder_df.Year==year)]
    filtered_df = filtered_df.sort_values(by="Population", ascending=False).head(15)

    fig = px.bar(filtered_df, x="Country", y="Population", color="Country",
                 title=f"Population — {continent} — {year}",
                 text_auto=True,
                 color_discrete_sequence=CATEGORY_COLORS)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      height=520,
                      margin={"t":40, "l":10, "r":10, "b":10},
                      template=DEFAULT_TEMPLATE,
                      font=dict(family="Inter, Arial, sans-serif", size=12))
    fig.update_traces(marker_line_width=0.5)
    return fig


def create_gdp_chart(continent="Asia", year=1952):
    filtered_df = gapminder_df[(gapminder_df.Continent==continent) & (gapminder_df.Year==year)]
    filtered_df = filtered_df.sort_values(by="GDP per Capita", ascending=False).head(15)

    fig = px.bar(filtered_df, x="Country", y="GDP per Capita", color="Country",
                 title=f"GDP per Capita — {continent} — {year}",
                 text_auto=True,
                 color_discrete_sequence=CATEGORY_COLORS)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      height=520,
                      margin={"t":40, "l":10, "r":10, "b":10},
                      template=DEFAULT_TEMPLATE,
                      font=dict(family="Inter, Arial, sans-serif", size=12))
    fig.update_traces(marker_line_width=0.5)
    return fig


def create_life_exp_chart(continent="Asia", year=1952):
    filtered_df = gapminder_df[(gapminder_df.Continent==continent) & (gapminder_df.Year==year)]
    filtered_df = filtered_df.sort_values(by="Life Expectancy", ascending=False).head(15)

    fig = px.bar(filtered_df, x="Country", y="Life Expectancy", color="Country",
                 title=f"Life Expectancy — {continent} — {year}",
                 text_auto=True,
                 color_discrete_sequence=CATEGORY_COLORS)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      height=520,
                      margin={"t":40, "l":10, "r":10, "b":10},
                      template=DEFAULT_TEMPLATE,
                      font=dict(family="Inter, Arial, sans-serif", size=12))
    fig.update_traces(marker_line_width=0.5)
    return fig


def create_choropleth_map(variable, year):
    filtered_df = gapminder_df[gapminder_df.Year==year]
    fig = px.choropleth(filtered_df,
                        color=variable,
                        locations="ISO Alpha Country Code",
                        locationmode="ISO-3",
                        color_continuous_scale=CONTINUOUS_MAP,
                        hover_data=["Country", variable],
                        title=f"{variable} Choropleth — {year}")
    fig.update_layout(dragmode=False,
                      paper_bgcolor="rgba(0,0,0,0)",
                      height=520,
                      margin={"l":0, "r":0, "b":0, "t":40},
                      template=DEFAULT_TEMPLATE,
                      font=dict(family="Inter, Arial, sans-serif", size=12))
    return fig

##################### WIDGETS ####################################
continents = sorted(gapminder_df.Continent.unique())
years = sorted(gapminder_df.Year.unique())

def mk_dropdown(id, options, value):
    return dcc.Dropdown(id=id, options=[{"label": o, "value": o} for o in options], value=value, clearable=False, style={"minWidth":"160px"})

cont_population = mk_dropdown("cont_pop", continents, "Asia")
year_population = mk_dropdown("year_pop", years, years[0])

cont_gdp = mk_dropdown("cont_gdp", continents, "Asia")
year_gdp = mk_dropdown("year_gdp", years, years[0])

cont_life_exp = mk_dropdown("cont_life_exp", continents, "Asia")
year_life_exp = mk_dropdown("year_life_exp", years, years[0])

year_map = mk_dropdown("year_map", years, years[0])
var_map = mk_dropdown("var_map", ["Population", "GDP per Capita", "Life Expectancy"], "Life Expectancy")

##################### APP LAYOUT ####################################
app.layout = html.Div([
    html.Div([
        html.H1("Gapminder Dataset Analysis", className="text-center fw-bold m-2"),
        html.P("Made it more colorful and added a download button", className="text-center text-muted mb-3"),
        dcc.Tabs([
            dcc.Tab([
                html.Br(),
                html.Div([
                    html.Div([
                        html.Button("Download full dataset (CSV)", id="btn-download-dataset", className="btn btn-sm btn-primary me-2"),
                        dcc.Download(id="download-dataset")
                    ], className="mb-2"),
                    dcc.Graph(id="dataset", figure=create_table())
                ])
            ], label="Dataset"),
            dcc.Tab([
                html.Br(),
                html.Div(className="d-flex align-items-center gap-2 mb-2", children=[
                    html.Div(["Continent", cont_population], style={"marginRight":"12px"}),
                    html.Div(["Year", year_population]),
                    html.Div(html.Button("Download visible (CSV)", id="btn-download-pop", className="btn btn-sm btn-outline-primary ms-3")),
                    dcc.Download(id="download-pop")
                ]),
                dcc.Graph(id="population", figure=create_population_chart())
            ], label="Population"),
            dcc.Tab([
                html.Br(),
                html.Div(className="d-flex align-items-center gap-2 mb-2", children=[
                    html.Div(["Continent", cont_gdp], style={"marginRight":"12px"}),
                    html.Div(["Year", year_gdp]),
                    html.Div(html.Button("Download visible (CSV)", id="btn-download-gdp", className="btn btn-sm btn-outline-primary ms-3")),
                    dcc.Download(id="download-gdp")
                ]),
                dcc.Graph(id="gdp", figure=create_gdp_chart())
            ], label="GDP Per Capita"),
            dcc.Tab([
                html.Br(),
                html.Div(className="d-flex align-items-center gap-2 mb-2", children=[
                    html.Div(["Continent", cont_life_exp], style={"marginRight":"12px"}),
                    html.Div(["Year", year_life_exp]),
                    html.Div(html.Button("Download visible (CSV)", id="btn-download-life", className="btn btn-sm btn-outline-primary ms-3")),
                    dcc.Download(id="download-life")
                ]),
                dcc.Graph(id="life_expectancy", figure=create_life_exp_chart())
            ], label="Life Expectancy"),
            dcc.Tab([
                html.Br(),
                html.Div(className="d-flex align-items-center gap-2 mb-2", children=[
                    html.Div(["Variable", var_map], style={"marginRight":"12px"}),
                    html.Div(["Year", year_map]),
                    html.Div(html.Button("Download visible (CSV)", id="btn-download-map", className="btn btn-sm btn-outline-primary ms-3")),
                    dcc.Download(id="download-map")
                ]),
                dcc.Graph(id="choropleth_map", figure=create_choropleth_map("Life Expectancy", years[0]))
            ], label="Choropleth Map"),
        ])
    ], className="col-10 mx-auto p-4 shadow-sm rounded", style={
        "background":"linear-gradient(180deg,#f8fafc 0%, #e9f0fb 100%)",
        "marginTop":"18px"
    })
], style={"background-color": "#dfeefb", "minHeight": "100vh"})

##################### CALLBACKS: UPDATE CHARTS ####################################
@callback(Output("population", "figure"), [Input("cont_pop", "value"), Input("year_pop", "value")])
def update_population_chart(continent, year):
    return create_population_chart(continent, year)

@callback(Output("gdp", "figure"), [Input("cont_gdp", "value"), Input("year_gdp", "value")])
def update_gdp_chart(continent, year):
    return create_gdp_chart(continent, year)

@callback(Output("life_expectancy", "figure"), [Input("cont_life_exp", "value"), Input("year_life_exp", "value")])
def update_life_exp_chart(continent, year):
    return create_life_exp_chart(continent, year)

@callback(Output("choropleth_map", "figure"), [Input("var_map", "value"), Input("year_map", "value")])
def update_map(var_map, year):
    return create_choropleth_map(var_map, year)

##################### CALLBACKS: DOWNLOADS ####################################
# Full dataset download
@callback(Output("download-dataset", "data"), [Input("btn-download-dataset", "n_clicks")])
def download_full_dataset(n_clicks):
    if not n_clicks:
        return None
    return dcc.send_data_frame(gapminder_df.to_csv, "gapminder_full.csv", index=False)

# Population tab download (current filters)
@callback(Output("download-pop", "data"),
          [Input("btn-download-pop", "n_clicks"), Input("cont_pop", "value"), Input("year_pop", "value")])
def download_population(n_clicks, continent, year):
    if not n_clicks:
        return None
    df = gapminder_df[(gapminder_df.Continent==continent) & (gapminder_df.Year==year)].sort_values(by="Population", ascending=False)
    return dcc.send_data_frame(df.to_csv, f"population_{continent}_{year}.csv", index=False)

# GDP tab download
@callback(Output("download-gdp", "data"),
          [Input("btn-download-gdp", "n_clicks"), Input("cont_gdp", "value"), Input("year_gdp", "value")])
def download_gdp(n_clicks, continent, year):
    if not n_clicks:
        return None
    df = gapminder_df[(gapminder_df.Continent==continent) & (gapminder_df.Year==year)].sort_values(by="GDP per Capita", ascending=False)
    return dcc.send_data_frame(df.to_csv, f"gdp_{continent}_{year}.csv", index=False)

# Life Expectancy tab download
@callback(Output("download-life", "data"),
          [Input("btn-download-life", "n_clicks"), Input("cont_life_exp", "value"), Input("year_life_exp", "value")])
def download_life(n_clicks, continent, year):
    if not n_clicks:
        return None
    df = gapminder_df[(gapminder_df.Continent==continent) & (gapminder_df.Year==year)].sort_values(by="Life Expectancy", ascending=False)
    return dcc.send_data_frame(df.to_csv, f"life_expectancy_{continent}_{year}.csv", index=False)

# Map tab download (variable + year)
@callback(Output("download-map", "data"),
          [Input("btn-download-map", "n_clicks"), Input("var_map", "value"), Input("year_map", "value")])
def download_map(n_clicks, var, year):
    if not n_clicks:
        return None
    df = gapminder_df[gapminder_df.Year==year][["Country", "Continent", "Year", var, "ISO Alpha Country Code"]]
    return dcc.send_data_frame(df.to_csv, f"choropleth_{var.replace(' ','_')}_{year}.csv", index=False)

##################### RUN ####################################
if __name__ == "__main__":
    app.run(debug=True)
