
# Live CTA Train Tracker

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
from bokeh.models import ColumnDataSource, CategoricalColorMapper, HoverTool, WheelZoomTool, CDSView, BooleanFilter
from bokeh.models.sources import AjaxDataSource
from bokeh.layouts import gridplot
import shapefile

# Create pages
app = Flask(__name__)

@app.route('/')
def show_dashboard():
    plots = []
    plots.append(make_plot())

    return render_template('layout.html', plots=plots)

@app.route('/mobile')
def show_dashboard_mobile():
    plots = []
    plots.append(make_plot_mobile())

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

    # Initialize Plot
    plot = figure(x_range=(-9790000, -9745000), y_range=(5120000, 5170000),x_axis_type="mercator", y_axis_type="mercator",tools=['pan'],sizing_mode='stretch_both')
    plot.add_tile(CARTODBPOSITRON)

    plot.toolbar.active_scroll = "auto"
    plot.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    plot.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks

    plot.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    plot.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks

    plot.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    plot.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

    plot.toolbar.logo = None
    plot.toolbar_location = None

    # Read in train line data
    sf = shapefile.Reader("CTA_New/CTA_New")
    features = sf.shapeRecords()

    Lines = []
    Coords_x = []
    Coords_y = []
    for shape in features:
        Line = shape.record[5]
        Coord = shape.shape.points
        X_s = []
        Y_s = []
        for coord in Coord:
            Trans = merc(tuple(reversed(coord)))
            X_s.append(Trans[0])
            Y_s.append(Trans[1])
        Coords_x.append(X_s)
        Coords_y.append(Y_s)

    CTA_Lines = ['Red','G','Blue','P','Brn','Pink','Org','Y']

    # Set up data sources
        # - Live CTA Data
    source = AjaxDataSource(data_url=request.url_root + 'cta_data/', polling_interval=5000, mode='replace')
    source.data = dict(x=[],y=[],next_station=[],destination=[],direction=[],color=[],line_name=[])

        # - Station Coordinate Data
    L_Map = pd.read_csv('Stations.csv')
    station_source = ColumnDataSource(dict(x=L_Map['coords_x'],y=L_Map['coords_y'],name=L_Map['STATION_NAME']))

    # Color Map for trains
    color_mapper = CategoricalColorMapper(factors= CTA_Lines, palette=['Red','Green','Blue','Purple','Brown','Pink','Orange','Yellow'])

    # Plot Glyphs
    for i in range(len(Coords_x)):
        plot.line(x=Coords_x[i],y=Coords_y[i],line_color="black",alpha=0.7)

    stations = plot.circle(x = 'x', y = 'y', source=station_source,size=5, line_color="black", fill_color = 'white')
    circles = plot.circle(x='x',y='y',angle='heading',source=source,color={'field': 'color', 'transform': color_mapper},size=14,line_color="black",line_width=0.8, legend='line_name')
    triangles = plot.triangle(x='x',y='y',angle='heading',source=source,size=8,color='white')

    # Set Up Tools
    hover = HoverTool(tooltips=[
        ("Next Stop", "@next_station"),
        ("Destination","@destination")
    ],renderers=[circles])

    station_hover = HoverTool(tooltips=[
        ("Station", "@name")
    ],renderers=[stations])

    wheel = WheelZoomTool()

    plot.add_tools(hover)
    plot.add_tools(station_hover)
    plot.add_tools(wheel)

    plot.toolbar.active_scroll = wheel

    plot.legend.location = "top_left"

    script, div = components(plot)
    return script, div

# Plot Generator
def make_plot_mobile():

    # Initialize Plot
    plot = figure(x_range=(-9790000, -9745000), y_range=(5120000, 5170000),x_axis_type="mercator", y_axis_type="mercator",tools=['pan'],sizing_mode='stretch_both')
    plot.add_tile(CARTODBPOSITRON)

    plot.toolbar.active_scroll = "auto"
    plot.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
    plot.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks

    plot.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
    plot.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks

    plot.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
    plot.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels

    plot.toolbar.logo = None
    plot.toolbar_location = None

    # Read in train line data
    sf = shapefile.Reader("CTA_New/CTA_New")
    features = sf.shapeRecords()

    Lines = []
    Coords_x = []
    Coords_y = []
    for shape in features:
        Line = shape.record[5]
        Coord = shape.shape.points
        X_s = []
        Y_s = []
        for coord in Coord:
            Trans = merc(tuple(reversed(coord)))
            X_s.append(Trans[0])
            Y_s.append(Trans[1])
        Coords_x.append(X_s)
        Coords_y.append(Y_s)

    CTA_Lines = ['Red','G','Blue','P','Brn','Pink','Org','Y']

    # Set up data sources
        # - Live CTA Data
    source = AjaxDataSource(data_url=request.url_root + 'cta_data/', polling_interval=5000, mode='replace')
    source.data = dict(x=[],y=[],next_station=[],destination=[],direction=[],color=[],line_name=[])

        # - Station Coordinate Data
    L_Map = pd.read_csv('Stations.csv')
    station_source = ColumnDataSource(dict(x=L_Map['coords_x'],y=L_Map['coords_y'],name=L_Map['STATION_NAME']))

    # Color Map for trains
    color_mapper = CategoricalColorMapper(factors= CTA_Lines, palette=['Red','Green','Blue','Purple','Brown','Pink','Orange','Yellow'])

    # Plot Glyphs
    for i in range(len(Coords_x)):
        plot.line(x=Coords_x[i],y=Coords_y[i],line_color="black",alpha=1)

    stations = plot.circle(x = 'x', y = 'y', source=station_source,size=10, line_color="black", fill_color = 'white')
    circles = plot.circle(x='x',y='y',angle='heading',source=source,color={'field': 'color', 'transform': color_mapper},size=28,line_color="black",line_width=0.8, legend='line_name')
    triangles = plot.triangle(x='x',y='y',angle='heading',source=source,size=16,color='white')

    # Set Up Tools
    hover = HoverTool(tooltips="""
    <div>
    	<div>
    		<span style="font-size: 24px; font-weight: bold;">Next Stop: </span>
            <span style="font-size: 24px;">@next_station</span>
    	</div>
    	<div> 
    		<span style="font-size: 24px; font-weight: bold;">Destination: </span>
            <span style="font-size: 24px;">@destination</span>
        </div>
    </div>
    """,renderers=[circles])

    station_hover = HoverTool(tooltips="""
    <div>
    	<div>
    		<span style="font-size: 24px; font-weight: bold;">Station: </span>
            <span style="font-size: 24px;">@name</span>
    	</div>
    </div>
    """,renderers=[stations])

    wheel = WheelZoomTool()

    plot.add_tools(hover)
    plot.add_tools(station_hover)
    plot.add_tools(wheel)

    plot.toolbar.active_scroll = wheel

    plot.legend.location = "top_left"

    script, div = components(plot)
    return script, div

# Data endpoint to fetch CTA train data from the API
@app.route('/cta_data/', methods=['GET','POST'])
def data():
    CTA_Lines = ['Red','G','Blue','P','Brn','Pink','Org','Y']

    equiv = {'Red':'Red Line',
    'G':'Green Line',
    'Blue':'Blue Line',
    'P':'Purple Line',
    'Brn':'Brown Line',
    'Pink':'Pink Line',
    'Org':'Orange Line',
    'Y':'Yellow Line'}

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
    AllTrainData['Line_Name'] = AllTrainData['Color'].map(equiv)

    return jsonify(x=list(AllTrainData['coords_x']),
                   y=list(AllTrainData['coords_y']),
                   next_station=list(AllTrainData['nextStaNm']),
                   destination=list(AllTrainData['destNm']),
                   line_name=list(AllTrainData['Line_Name']),
                   heading=[math.radians(x) for x in list(AllTrainData['heading'])],
                   color=list(AllTrainData['Color']))

if __name__ == "__main__":
	app.run()