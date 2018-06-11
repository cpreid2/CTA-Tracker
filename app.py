from flask import render_template, jsonify, request
from flask import Flask

from bokeh.plotting import figure
from bokeh.embed import components

import pandas as pd
import requests
import json

import math
from ast import literal_eval

from bokeh.plotting import figure
from bokeh.tile_providers import CARTODBPOSITRON
from bokeh.models import ColumnDataSource, CategoricalColorMapper, HoverTool
from bokeh.models.sources import AjaxDataSource
from bokeh.layouts import gridplot

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/dashboard/')
def show_dashboard():
    plots = []
    plots.append(make_plot())

    return render_template('layout.html', plots=plots)

# Fucntion to convert lat and long to x and y
def merc(Coords):
    lat = Coords[0]
    lon = Coords[1]

    r_major = 6378137.000
    x = r_major * math.radians(lon)
    scale = x/lon
    y = 180.0/math.pi * math.log(math.tan(math.pi/4.0 + lat * (math.pi/180.0)/2.0)) * scale
    return (x, y)

# Plot Generator
def make_plot():

    CTA_Lines = ['Red','G','Blue','P','Brn','Pink','Org','Y']

    source = AjaxDataSource(data_url=request.url_root + 'cta_data/', polling_interval=5000, mode='replace')
    source.data = dict(x=[],y=[],next_station=[],destination=[],direction=[],color=[])


    color_mapper = CategoricalColorMapper(factors= CTA_Lines, palette=['Red','Green','Blue','Purple','Brown','Pink','Orange','Yellow'])

    hover = HoverTool(tooltips=[
        ("Next Stop", "@next_station"),
        ("Destination","@destination")

    ])

    plot = figure(title='Live CTA Tracker',x_range=(-9780000, -9745000), y_range=(5130000, 5160000),x_axis_type="mercator", y_axis_type="mercator",tools=[hover, 'wheel_zoom','pan'],sizing_mode='stretch_both')
    plot.add_tile(CARTODBPOSITRON)

    plot.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    plot.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks

    plot.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    plot.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks

    plot.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    plot.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

    circles = plot.circle(x='x',y='y', source=source,size=9,color={'field': 'color', 'transform': color_mapper})

    script, div = components(plot)
    return script, div


# Data endpoint to fetch CTA train data from the API
@app.route('/cta_data/', methods=['GET','POST'])
def data():
    CTA_Lines = ['Red','G','Blue','P','Brn','Pink','Org','Y']

    Train_Data = []
    for line in CTA_Lines:
        r = requests.get('http://lapi.transitchicago.com/api/1.0/ttpositions.aspx?key=XYZ&rt='+line+'&outputType=JSON')
        data = json.loads(r.text)
        try:
            trains = data['ctatt']['route'][0]['train']
            DF = pd.read_json(json.dumps(trains))
            DF['Color'] = line
            Train_Data.append(DF)
        except:
            pass

    AllTrainData = pd.concat(Train_Data, axis=0)
    AllTrainData.head()
    AllTrainData['coords_x'] = AllTrainData[['lat','lon']].apply(lambda x: merc(x)[0], axis=1)
    AllTrainData['coords_y'] = AllTrainData[['lat','lon']].apply(lambda x: merc(x)[1], axis=1)
    AllTrainData.fillna('',inplace=True)

    return jsonify(x=list(AllTrainData['coords_x']),
                   y=list(AllTrainData['coords_y']),
                   next_station=list(AllTrainData['nextStaNm']),
                   destination=list(AllTrainData['destNm']),
                   direction=list(AllTrainData['heading']),
                   color=list(AllTrainData['Color']))
