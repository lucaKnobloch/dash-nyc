import dash
import dash_core_components as dcc
import dash_html_components as html
import flask
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

data = pd.read_csv('merged.csv', index_col='Index')

# my own token
# mapbox_access_token = "pk.eyJ1IjoibHVjYWtub2Jsb2NoIiwiYSI6ImNrNHY2aWVzNDBqcDAzZW4xazU0anpoc2MifQ.FDBPUYpAp7UYwaP-UAa_WA"
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

hours = []
for i in range(24):
	if i < 10:
		hours.append('2017-01-28 0' + str(i) + ':00:0')
	else:
		hours.append('2017-01-28 ' + str(i) + ':00:0')

graph_hours = []
for i in range(24):
	graph_hours.append(hours[i].replace("2017-01-28 ", "").replace(":00:0", ":00"))

update_data = []
latitude = []
Longitude = []
for i in range(24):
	if i == 0:
		i = 1
		update_data.append(
			data.loc[(hours[i - 1] <= data['tpep_pickup_datetime']) & (data['tpep_pickup_datetime'] <= hours[i])])
	elif i < 23:
		update_data.append(
			data.loc[(hours[i] <= data['tpep_pickup_datetime']) & (data['tpep_pickup_datetime'] <= hours[i + 1])])
	else:
		update_data.append(data.loc[(hours[i] <= data['tpep_pickup_datetime'])])

sum_up_payment = []
sum_up_people_per_hour = []
latitude_for_hour = []
Longitude_for_hour = []

len_of_previous = 0
for i in range(24):
	latitude_in_hour = []
	Longitude_in_hour = []
	sum_up_payment.append(update_data[i]['payment_type'].value_counts())
	sum_up_people_per_hour.append(len(update_data[i]))

	for ii in range(len(update_data[i]['Latitude'])):
		ii += len_of_previous
		if (update_data[i]['Latitude'][ii] not in latitude_in_hour):
			latitude_in_hour.append(update_data[i]['Latitude'][ii])
		if (update_data[i]['Longitude'][ii] not in Longitude_in_hour):
			Longitude_in_hour.append(update_data[i]['Longitude'][ii])

	latitude_for_hour.append(latitude_in_hour)
	Longitude_for_hour.append(Longitude_in_hour)
	len_of_previous += (len(update_data[i]['Latitude']))

payment_1 = []
payment_2 = []
for i in range(24):
	payment_1.append(sum_up_payment[i][1])
	payment_2.append(sum_up_payment[i][2])

chart_data = pd.DataFrame(
	{'Hours': graph_hours,
	 'Amount_of_people': sum_up_people_per_hour,
	 'Payment_1': payment_1,
	 'Payment_2': payment_2,
	 'Longitude': Longitude_for_hour,
	 'Latitude': latitude_for_hour
	 })

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)
# Dictionary of important locations in New York
list_of_locations = {
	"Madison Square Garden": {"lat": 40.7505, "lon": -73.9934},
	"Yankee Stadium": {"lat": 40.8296, "lon": -73.9262},
	"Empire State Building": {"lat": 40.7484, "lon": -73.9857},
	"New York Stock Exchange": {"lat": 40.7069, "lon": -74.0113},
	"JFK Airport": {"lat": 40.644987, "lon": -73.785607},
	"Grand Central Station": {"lat": 40.7527, "lon": -73.9772},
	"Times Square": {"lat": 40.7589, "lon": -73.9851},
	"Columbia University": {"lat": 40.8075, "lon": -73.9626},
	"United Nations HQ": {"lat": 40.7489, "lon": -73.9680},
}

app.layout = html.Div(
	children=[
		html.Div([
			html.Div('Dash NYC', style={'fontSize': 30}),

			html.Div(
				className="row",
				children=[
					# Column for user controls
					html.Div(
						className="four columns div-user-controls",
						children=[
							html.P(
								"""Select different days using the date picker or by selecting 
								different time frames on the histogram."""
							),
							# Change to side-by-side for mobile layout
							html.Div(
								className="row",
								children=[
									html.Div(
										className="div-for-dropdown",
										children=[
											# Dropdown for locations on map
											dcc.Dropdown(
												id="location-dropdown",
												options=[
													{"label": i, "value": i}
													for i in list_of_locations
												],
												placeholder="Select a location",
											)
										],
									),
								],
							), html.Div(
								className="text-padding",
								children=[
									"Select any of the bars on the histogram to section data by time."
								],
							),
							html.Div(
								className="div-for-dropdown",
								children=[
									# Dropdown to select times
									dcc.Dropdown(
										id="hour-selector",
										options=[
											{
												"label": str(n) + ":00",
												"value": str(n),
											}
											for n in range(24)
										],
										multi=True,
										placeholder="Select certain hours",
									)
								],
							),
							html.P(id="total-rides"),
							html.P(id="total-rides-selection"),
							html.P(id="date-value"),

							dcc.Graph(id="histogram"),

						],
					),
					# Column for app graphs and plots
					html.Div(
						className="eight columns div-for-charts bg-grey",
						children=[
							dcc.Graph(id="map-graph"),

							dcc.Graph(
								figure=dict(
									data=[
										dict(
											x=chart_data['Hours'],
											y=chart_data['Payment_1'],
											name="Credit Card",
											marker=dict(
												color='rgb(55, 83, 109)'
											)
										),
										dict(
											x=chart_data['Hours'],
											y=chart_data['Payment_2'],
											name="Cash",
											marker=dict(
												color='rgb(26, 118, 255)'
											)
										)
									],
									layout=dict(
										xaxis={
											'rangeslider': {'visible': True},
											'rangeselector': {'visible': True,
											                  'buttons': [{'step': 'all'}, {'step': 'day'},
											                              {'step': 'hour'}]}
										}, title_text="Payment",
										showlegend=True,
										legend=dict(
											x=0,
											y=1.0
										),
										margin=dict(l=15, r=15, t=15, b=15)
									)
								),
								style={"height": "100%", "width": "100%"}

							)
						],
					),
				],
			)
		], style={'marginBottom': 15, 'marginTop': 15, 'marginLeft': 15, 'marginRight': 15}),
	]
)


# Get the amount of rides per hour based on the time selected
# This also higlights the color of the histogram bars based on
# if the hours are selected
def get_selection(selection):
	xVal = []
	yVal = []
	xSelected = []
	colorVal = [
		"#F4EC15",
		"#DAF017",
		"#BBEC19",
		"#9DE81B",
		"#80E41D",
		"#66E01F",
		"#4CDC20",
		"#34D822",
		"#24D249",
		"#25D042",
		"#26CC58",
		"#28C86D",
		"#29C481",
		"#2AC093",
		"#2BBCA4",
		"#2BB5B8",
		"#2C99B4",
		"#2D7EB0",
		"#2D65AC",
		"#2E4EA4",
		"#2E38A4",
		"#3B2FA0",
		"#4E2F9C",
		"#603099",
	]

	# Put selected times into a list of numbers xSelected
	if selection is not None:
		xSelected.extend([int(x) for x in selection])
	for i in range(24):
		# If bar is selected then color it white
		if i in xSelected and len(xSelected) < 24:
			colorVal[i] = "#FFFFFF"
		xVal.append(i)
		# Get the number of rides at a particular time
		yVal.append(chart_data['Amount_of_people'][i])
	return [np.array(xVal), np.array(yVal), np.array(colorVal)]


# Selected Data in the Histogram updates the Values in the hour selector
@app.callback(
	Output("hour-selector", "value"),
	[Input("histogram", "selectedData"), Input("histogram", "clickData")],
)
def update_bar_selector(value, clickData):
	holder = []
	if clickData:
		holder.append(str(int(clickData["points"][0]["x"])))
	if value:
		for x in value["points"]:
			holder.append(str(int(x["x"])))
	return list(set(holder))


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
	if clickData:
		return {"points": []}


# Update the total number of rides Tag
@app.callback(Output("total-rides", "children"), [Input("hour-selector", "value")])
def update_total_rides(hourPicked):
	if hourPicked is not None:
		if len(hourPicked) == 1:
			hourPicked = hourPicked[0].replace(':00', '')
			selected_people = chart_data['Amount_of_people'][int(hourPicked)]
			return "Total Number of rides: {}".format(str(selected_people))

		if len(hourPicked) > 1:
			picked = []
			totalamount = 0
			for i in range(len(hourPicked)):
				picked.append(hourPicked[i].replace(':00', ''))
			for ii in range(len(picked)):
				totalamount += chart_data['Amount_of_people'][int(picked[ii])]
			return "Total Number of rides: {}".format(totalamount)


# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
	Output("histogram", "figure"),
	[Input("hour-selector", "value")],
)
def update_histogram(hour_selection):
	[xVal, yVal, colorVal] = get_selection(hour_selection)

	layout = go.Layout(
		bargap=0.01,
		bargroupgap=0,
		barmode="group",
		margin=go.layout.Margin(l=10, r=0, t=0, b=50),
		showlegend=False,
		plot_bgcolor="#323130",
		paper_bgcolor="#323130",
		dragmode="select",
		font=dict(color="white"),
		xaxis=dict(
			range=[-0.5, 23.5],
			showgrid=False,
			nticks=25,
			fixedrange=True,
			ticksuffix=":00",
		),
		yaxis=dict(
			range=[0, max(yVal) + max(yVal) / 4],
			showticklabels=False,
			showgrid=False,
			fixedrange=True,
			rangemode="nonnegative",
			zeroline=False,
		),
		annotations=[
			dict(
				x=xi,
				y=yi,
				text=str(yi),
				xanchor="center",
				yanchor="bottom",
				showarrow=True,
				font=dict(color="white"),
			)
			for xi, yi in zip(xVal, yVal)
		],
	)

	return go.Figure(
		data=[
			go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
			go.Scatter(
				opacity=0,
				x=xVal,
				y=yVal / 2,
				hoverinfo="none",
				mode="markers",
				marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
				visible=True,
			),
		],
		layout=layout,
	)


# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
	Output("map-graph", "figure"),
	[
		Input("hour-selector", "value"),
		Input("location-dropdown", "value"),
	],
)
def update_graph(selectedData, selectedLocation):
	zoom = 12.0
	latInitial = 40.7272
	lonInitial = -73.991251
	bearing = 0

	if selectedLocation:
		zoom = 15.0
		latInitial = list_of_locations[selectedLocation]["lat"]
		lonInitial = list_of_locations[selectedLocation]["lon"]

	long, lat = getLatLonColor(selectedData)
	return go.Figure(
		data=[
			# Data for all rides based on date and time
			go.Scattermapbox(
				lat=lat,
				lon=long,
				mode="markers",
				hoverinfo="lat+lon+text",
				text=chart_data['Hours'],
				marker=dict(
					showscale=False,
					# color=np.append(np.insert(len(chart_data['Hours']), 0, 0), 23),
					opacity=0.5,
					size=10,
					colorscale=[
						[0, "#F4EC15"],
						[0.04167, "#DAF017"],
						[0.0833, "#BBEC19"],
						[0.125, "#9DE81B"],
						[0.1667, "#80E41D"],
						[0.2083, "#66E01F"],
						[0.25, "#4CDC20"],
						[0.292, "#34D822"],
						[0.333, "#24D249"],
						[0.375, "#25D042"],
						[0.4167, "#26CC58"],
						[0.4583, "#28C86D"],
						[0.50, "#29C481"],
						[0.54167, "#2AC093"],
						[0.5833, "#2BBCA4"],
						[1.0, "#613099"],
					],
					colorbar=dict(
						title="Time of<br>Day",
						x=0.93,
						xpad=0,
						nticks=24,
						tickfont=dict(color="#d8d8d8"),
						titlefont=dict(color="#d8d8d8"),
						thicknessmode="pixels",
					),
				),
			),
			# Plot of important locations on the map
			go.Scattermapbox(
				lat=[list_of_locations[i]["lat"] for i in list_of_locations],
				lon=[list_of_locations[i]["lon"] for i in list_of_locations],
				mode="markers",
				hoverinfo="text",
				text=[i for i in list_of_locations],
				marker=dict(size=8, color="#ffa0a0"),
			),
		],
		layout=go.Layout(
			autosize=True,
			margin=dict(l=15, r=15, t=15, b=15),
			showlegend=False,
			mapbox=dict(
				accesstoken=mapbox_access_token,
				center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
				style="dark",
				bearing=bearing,
				zoom=zoom,
			),
			updatemenus=[
				dict(
					buttons=(
						[
							dict(
								args=[
									{
										"mapbox.zoom": 12,
										"mapbox.center.lon": "-73.991251",
										"mapbox.center.lat": "40.7272",
										"mapbox.bearing": 0,
										"mapbox.style": "dark",
									}
								],
								label="Reset Zoom",
								method="relayout",
							)
						]
					),
					direction="left",
					pad={"r": 0, "t": 0, "b": 0, "l": 0},
					showactive=False,
					type="buttons",
					x=0.45,
					y=0.02,
					xanchor="left",
					yanchor="bottom",
					bgcolor="#323130",
					borderwidth=1,
					bordercolor="#6d6d6d",
					font=dict(color="#FFFFFF"),
				)
			],
		),
	)


# Get the Coordinates of the chosen months, dates and times
def getLatLonColor(selectedData):
	longCoords = []
	latCoords = []
	# No times selected, output all times for chosen month and date
	if selectedData is None or len(selectedData) is 0:
		for i in range(24):
			latCoords.extend(chart_data['Latitude'][int(i)])
			longCoords.extend(chart_data['Longitude'][int(i)])

	elif len(selectedData) == 1:
		for i in selectedData:
			latCoords = chart_data['Latitude'][int(i)]
			longCoords = chart_data['Longitude'][int(i)]

	elif len(selectedData) > 1 :
		for i in selectedData:
			latCoords.extend(chart_data['Latitude'][int(i)])
			longCoords.extend(chart_data['Longitude'][int(i)])
	return longCoords, latCoords

if __name__ == "__main__":
	app.run_server(debug=True)
