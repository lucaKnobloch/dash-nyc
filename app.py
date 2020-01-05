import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go

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
for i in range(24):
	sum_up_payment.append(update_data[i]['payment_type'].value_counts())
	sum_up_people_per_hour.append(len(update_data[i]))

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
	 })

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
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
									id="bar-selector",
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
						dcc.Graph(
							id='example-graph',
							figure={
								'data': [
									{'x': chart_data['Hours'], 'y': chart_data['Amount_of_people'], 'type': 'bar'},
								], 'layout': {
									'clickmode': 'select+event',
									'margin': dict(l=15, r=15, t=15, b=15),
								}
							},
							style={"height": "50%", "width": "100%"},
						)

					],
				),
				# Column for app graphs and plots
				html.Div(
					className="eight columns div-for-charts bg-grey",
					children=[
						dcc.Graph(
							figure=dict(
								data=[
									# Data for all rides based on date and time
									go.Scattermapbox(
										# lat=data['Latitude'],
										# lon=data['Longitude'],
										mode='markers',
										hoverinfo="lat + lon + text",
										marker=go.scattermapbox.Marker(
											size=14
										),
										text=['Zones'],
									),
								],
								layout=dict(
									autosize=True,
									margin=go.layout.Margin(l=15, r=15, t=15, b=15),
									mapbox=dict(
										accesstoken=mapbox_access_token,
										center=dict(lat=40.7272, lon=-73.991251),
										style="dark",
										pitch=0,
										zoom=10
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
								)),
							style={"height": "100%", "width": "100%"}
						),


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
								'rangeselector': {'visible': True, 'buttons': [{'step': 'all'}, {'step': 'day'},
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

if __name__ == "__main__":
	app.run_server(debug=True)
