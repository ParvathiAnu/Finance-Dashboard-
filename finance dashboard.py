import math
import datetime as dt
import numpy as np
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import TextInput, Button, DatePicker, MultiChoice

API_KEY = 'TT992S59LCHVQDCT'

def load_data(ticker1, ticker2, start, end):
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    
    df1, _ = ts.get_daily_adjusted(symbol=ticker1, outputsize='full')
    df2, _ = ts.get_daily_adjusted(symbol=ticker2, outputsize='full')
    
    df1 = df1.loc[start:end]
    df2 = df2.loc[start:end]
    
    df1.columns = [col.split('. ')[1] for col in df1.columns]
    df2.columns = [col.split('. ')[1] for col in df2.columns]
    
    df1.index = pd.to_datetime(df1.index)
    df2.index = pd.to_datetime(df2.index)

    return df1, df2

def update_plot(data, indicators, sync_axis=None):
    df = data
    gain = df['close'] > df['open']
    loss = df['open'] > df['close']
    width = 12 * 60 * 60 * 1000

    if sync_axis is not None:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000, x_range=sync_axis)
    else:
        p = figure(x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", width=1000)

    p.xaxis.major_label_orientation = math.pi / 4
    p.grid.grid_line_alpha = 0.3

    p.segment(df.index, df['high'], df.index, df['low'], color="black")
    p.vbar(df.index[gain], width, df['open'][gain], df['close'][gain], fill_color="#00ff00", line_color="#00ff00")
    p.vbar(df.index[loss], width, df['open'][loss], df['close'][loss], fill_color="#ff0000", line_color="#ff0000")

    for indicator in indicators:
        if indicator == "30 Day SMA":
            df['SMA30'] = df['close'].rolling(30).mean()
            p.line(df.index, df['SMA30'], color="purple", legend_label="30 Day SMA")
        elif indicator == "100 Day SMA":
            df['SMA100'] = df['close'].rolling(100).mean()
            p.line(df.index, df['SMA100'], color="blue", legend_label="100 Day SMA")
        elif indicator == "Linear Regression Line":
            par = np.polyfit(range(len(df.index.values)), df['close'].values, 1, full=True)
            slope = par[0][0]
            intercept = par[0][1]
            y_predicted = [slope * i + intercept for i in range(len(df.index.values))]
            p.segment(df.index[0], y_predicted[0], df.index[-1], y_predicted[-1], legend_label="Linear Regression",
                      color="red")

    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    return p

def on_button_click(main_stock, comparison_stock, start, end, indicators):
    source1, source2 = load_data(main_stock, comparison_stock, start, end)
    p = update_plot(source1, indicators)
    p2 = update_plot(source2, indicators, sync_axis=p.x_range)
    curdoc().clear()
    curdoc().add_root(layout)
    curdoc().add_root(row(p, p2))

stock1_text = TextInput(title="Main Stock")
stock2_text = TextInput(title="Comparison Stock")
date_picker_from = DatePicker(title='Start Date', value="2020-01-01", min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))
date_picker_to = DatePicker(title='End Date', value="2020-02-01", min_date="2000-01-01", max_date=dt.datetime.now().strftime("%Y-%m-%d"))
indicator_choice = MultiChoice(options=["100 Day SMA", "30 Day SMA", "Linear Regression Line"])

load_button = Button(label="Load Data", button_type="success")
load_button.on_click(lambda: on_button_click(stock1_text.value, stock2_text.value, date_picker_from.value, date_picker_to.value, indicator_choice.value))

layout = column(stock1_text, stock2_text, date_picker_from, date_picker_to, indicator_choice, load_button)

curdoc().clear()
curdoc().add_root(layout)
