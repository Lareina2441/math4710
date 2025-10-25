# app.py
from dash import Dash, dcc, html, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ----- app & css -----
css = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css"]
app = Dash(__name__, external_stylesheets=css)
server = app.server

# ----- data -----
gapminder_df = px.data.gapminder()  # 内置 gapminder 数据
# 规范列名为更易读的形式
gapminder_df = gapminder_df.rename(columns={
    "country": "Country",
    "continent": "Continent",
    "year": "Year",
    "lifeExp": "Life Expectancy",
    "pop": "Population",
    "gdpPercap": "GDP per Capita",
    "iso_alpha": "ISO-3"
})
# 有的 plotly 版本可能没有 iso_alpha 列：如果缺少则生成 NaN（choropleth 可能不全）
if "ISO-3" not in gapminder_df.columns:
    gapminder_df["ISO-3"] = None

continents = sorted(gapminder_df.Continent.unique().tolist())
years = sorted(gapminder_df.Year.unique().tolist())

# ----- figure factories -----
def create_table_figure(df: pd.DataFrame, height=400):
    # 使用 go.Table 来显示（和你原代码风格接近）
    header_vals = list(df.columns)
    cell_vals = [df[col].astype(str).tolist() for col in df.columns]
    fig = go.Figure(data=[go.Table(
        header=dict(values=header_vals, align='left', fill_color="#dfe6f0"),
        cells=dict(values=cell_vals, align='left')
    )])
    fig.update_layout(margin={"t": 0, "l": 0, "r": 0, "b": 0}, height=height, paper_bgcolor="#ffffff")
    return fig

def create_population_chart(continent="Asia", year=1952):
    filtered_df = gapminder_df[(gapminder_df.Continent == continent) & (gapminder_df.Year == int(year))]
    filtered_df = filtered_df.sort_values(by="Population", ascending=False).head(15)
    fig = px.bar(filtered_df, x="Country", y="Population", color="Country",
                 title=f"Top 15 Population — {continent} — {year}", text_auto=True)
    fig.update_layout(paper_bgcolor="#e5ecf6", height=500, margin={"t":40})
    return fig

def create_gdp_chart(continent="Asia", year=1952):
    filtered_df = gapminder_df[(gapminder_df.Continent == continent) & (gapminder_df.Year == int(year))]
    filtered_df = filtered_df.sort_values(by="GDP per Capita", ascending=False).head(15)
    fig = px.bar(filtered_df, x="Country", y="GDP per Capita", color="Country",
                 title=f"Top 15 GDP per Capita — {continent} — {year}", text_auto=True)
    fig.update_layout(paper_bgcolor="#e5ecf6", height=500, margin={"t":40})
    return fig

def create_life_exp_chart(continent="Asia", year=1952):
    filtered_df = gapminder_df[(gapminder_df.Continent == continent) & (gapminder_df.Year == int(year))]
    filtered_df = filtered_df.sort_values(by="Life Expectancy", ascending=False).head(15)
    fig = px.bar(filtered_df, x="Country", y="Life Expectancy", color="Country",
                 title=f"Top 15 Life Expectancy — {continent} — {year}", text_auto=True)
    fig.update_layout(paper_bgcolor="#e5ecf6", height=500, margin={"t":40})
    return fig

def create_choropleth_map(variable="Life Expectancy", year=1952):
    # 变量映射
    var_map = {
        "Population": "Population",
        "GDP per Capita": "GDP per Capita",
        "Life Expectancy": "Life Expectancy"
    }
    col = var_map.get(variable, variable)
    filtered_df = gapminder_df[gapminder_df.Year == int(year)].copy()
    # 若没有 ISO-3 列，用 Country 名称（效果差一些，但避免报错）
    if filtered_df.get("ISO-3").notna().any():
        locations = "ISO-3"
        locationmode = "ISO-3"
    else:
        locations = "Country"
        locationmode = None  # plotly 会尝试匹配国家名

    fig = px.choropleth(filtered_df,
                        locations=locations,
                        color=col,
                        hover_name="Country",
                        title=f"{col} Choropleth — {year}",
                        color_continuous_scale="RdYlBu")
    fig.update_layout(paper_bgcolor="#e5ecf6", height=500, margin={"t":40})
    return fig

# ----- layout -----
app.layout = html.Div([
    html.Div([
        html.H1("Gapminder Dashboard", className="text-center fw-bold my-3"),
        html.Div(className="row", children=[
            # 左侧菜单
            html.Div(className="col-3", children=[
                html.Div([
                    html.H5("Views", className="fw-bold"),
                    dcc.RadioItems(
                        id="view-selector",
                        options=[
                            {"label": "Dataset", "value": "Dataset"},
                            {"label": "Population", "value": "Population"},
                            {"label": "GDP per Capita", "value": "GDP"},
                            {"label": "Life Expectancy", "value": "Life"},
                            {"label": "Choropleth Map", "value": "Map"},
                        ],
                        value="Dataset",
                        labelStyle={"display": "block", "padding": "6px 0"}
                    ),
                    html.Hr(),
                    html.Div(id="help-text", children="点击左侧视图可切换并显示对应下拉菜单与表格/图表。")
                ], style={"position": "sticky", "top": "10px"})
            ]),
            # 右侧主区
            html.Div(className="col-9", children=[
                # 动态控件区域（根据视图显示不同下拉）
                html.Div(id="controls-div", className="mb-3"),
                # 主图表区域
                dcc.Graph(id="main-graph"),
                html.Hr(),
                html.H5("Data (table)"),
                dcc.Graph(id="dataset-graph")
            ])
        ])
    ], className="container-fluid", style={"background-color": "#e5ecf6", "minHeight": "95vh", "padding": "20px"})
])

# ----- callbacks -----
@callback(
    Output("controls-div", "children"),
    Input("view-selector", "value")
)
def render_controls(view):
    """根据左侧菜单渲染对应下拉菜单（显示/隐藏逻辑由此完成）。"""
    # 通用下拉组件生成函数
    def continent_dd(id_):
        return dcc.Dropdown(id=id_, options=[{"label": c, "value": c} for c in continents],
                            value=continents[0], clearable=False, style={"width": "220px", "display": "inline-block", "marginRight":"10px"})

    def year_dd(id_):
        return dcc.Dropdown(id=id_, options=[{"label": y, "value": y} for y in years],
                            value=years[0], clearable=False, style={"width": "140px", "display": "inline-block", "marginRight":"10px"})

    if view == "Dataset":
        # 仅显示说明或可选的过滤（这里我们显示年份过滤做示范）
        return html.Div([
            html.Span("（Dataset）显示完整数据或按年份过滤：", className="me-2"),
            year_dd("dataset_year")
        ])
    elif view == "Population":
        return html.Div([
            html.Span("Continent: ", className="me-2"),
            continent_dd("cont_pop"),
            html.Span("Year: ", className="me-2"),
            year_dd("year_pop")
        ])
    elif view == "GDP":
        return html.Div([
            html.Span("Continent: ", className="me-2"),
            continent_dd("cont_gdp"),
            html.Span("Year: ", className="me-2"),
            year_dd("year_gdp")
        ])
    elif view == "Life":
        return html.Div([
            html.Span("Continent: ", className="me-2"),
            continent_dd("cont_life"),
            html.Span("Year: ", className="me-2"),
            year_dd("year_life")
        ])
    elif view == "Map":
        return html.Div([
            dcc.Dropdown(id="var_map", options=[
                {"label": "Population", "value": "Population"},
                {"label": "GDP per Capita", "value": "GDP per Capita"},
                {"label": "Life Expectancy", "value": "Life Expectancy"}],
                value="Life Expectancy", clearable=False, style={"width":"220px", "display":"inline-block", "marginRight":"10px"}),
            html.Span("Year: ", className="me-2"),
            dcc.Dropdown(id="year_map", options=[{"label": y, "value": y} for y in years],
                         value=years[0], clearable=False, style={"width":"140px", "display":"inline-block"})
        ])
    else:
        return html.Div()  # never hits

# 主图和表格的更新：将根据当前视图与控件值更新
@callback(
    Output("main-graph", "figure"),
    Output("dataset-graph", "figure"),
    Input("view-selector", "value"),
    # 下面是所有可能会被渲染出来的控件（即使未渲染，其值也会传入；Dash 在未挂载元素时不会提供值，
    # 所以使用防守式取值）
    Input("cont_pop", "value"),
    Input("year_pop", "value"),
    Input("cont_gdp", "value"),
    Input("year_gdp", "value"),
    Input("cont_life", "value"),
    Input("year_life", "value"),
    Input("var_map", "value"),
    Input("year_map", "value"),
    Input("dataset_year", "value"),
)
def update_main_and_table(view,
                          cont_pop, year_pop,
                          cont_gdp, year_gdp,
                          cont_life, year_life,
                          var_map, year_map,
                          dataset_year):
    # default figures (empty)
    empty_fig = go.Figure()
    empty_fig.update_layout(height=400, paper_bgcolor="#e5ecf6")
    # 默认表格为完整 dataset
    table_fig = create_table_figure(gapminder_df, height=400)

    # defensive fallbacks: 如果 None 则使用首个值
    if year_pop is None and len(years)>0: year_pop = years[0]
    if year_gdp is None and len(years)>0: year_gdp = years[0]
    if year_life is None and len(years)>0: year_life = years[0]
    if year_map is None and len(years)>0: year_map = years[0]
    if dataset_year is None and len(years)>0: dataset_year = years[0]
    if cont_pop is None and len(continents)>0: cont_pop = continents[0]
    if cont_gdp is None and len(continents)>0: cont_gdp = continents[0]
    if cont_life is None and len(continents)>0: cont_life = continents[0]
    if var_map is None: var_map = "Life Expectancy"

    # 根据视图选择主图和表格展示内容
    try:
        if view == "Dataset":
            # 如果选择按年份过滤 dataset，则展示该年的全部数据，否则全部数据
            df = gapminder_df.copy()
            if dataset_year:
                df = df[df.Year == int(dataset_year)]
            table_fig = create_table_figure(df, height=500)
            main_fig = create_table_figure(df, height=500)  # 主区也可以显示同一个表格（或设置为 empty）
            return main_fig, table_fig

        elif view == "Population":
            main_fig = create_population_chart(cont_pop, year_pop)
            # 表格：展示被用于绘图的条目（前 15）
            df = gapminder_df[(gapminder_df.Continent == cont_pop) & (gapminder_df.Year == int(year_pop))]
            df = df.sort_values("Population", ascending=False).head(15)
            table_fig = create_table_figure(df, height=320)
            return main_fig, table_fig

        elif view == "GDP":
            main_fig = create_gdp_chart(cont_gdp, year_gdp)
            df = gapminder_df[(gapminder_df.Continent == cont_gdp) & (gapminder_df.Year == int(year_gdp))]
            df = df.sort_values("GDP per Capita", ascending=False).head(15)
            table_fig = create_table_figure(df, height=320)
            return main_fig, table_fig

        elif view == "Life":
            main_fig = create_life_exp_chart(cont_life, year_life)
            df = gapminder_df[(gapminder_df.Continent == cont_life) & (gapminder_df.Year == int(year_life))]
            df = df.sort_values("Life Expectancy", ascending=False).head(15)
            table_fig = create_table_figure(df, height=320)
            return main_fig, table_fig

        elif view == "Map":
            main_fig = create_choropleth_map(var_map, year_map)
            df = gapminder_df[gapminder_df.Year == int(year_map)]
            # 表格：展示用于地图的该年全部数据的前 50 条（避免过长）
            table_fig = create_table_figure(df.head(50), height=300)
            return main_fig, table_fig

        else:
            return empty_fig, table_fig
    except Exception as e:
        # 出错时显示空图并在表格里显示错误信息（便于 debug）
        err_df = pd.DataFrame({"Error": [str(e)]})
        return empty_fig, create_table_figure(err_df, height=200)

# ----- run -----
if __name__ == "__main__":
    app.run(debug=True)
