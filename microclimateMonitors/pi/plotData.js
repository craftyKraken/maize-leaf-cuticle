function plotData(data) {
	
	//data = data.slice(0,10);
	
	var tempPoints = [];
	var rhPoints = [];
	var now = Math.floor(Date.now() / 1000);
	var ago = now - 3600*5 // fit window to 5 hours ago
	
	for (var i=0; i < data.length; i++) {
		var tempPoint = [ data[i][1], data[i][2] ]
		var rhPoint = [ data[i][1], data[i][3] ]
		tempPoints.push(tempPoint);
		rhPoints.push(rhPoint);
	}

	
	Flotr.draw(
		document.getElementById("rhPlot"),
		[
			{
				data: rhPoints,
				label: "Relative Humidity (%)",
				points: {show:true}
			},
			{
				data: tempPoints,
				yaxis: 2,
				label: "Temperature (C)",
				points: {show:true}
			}
		],
		{
			title: "Real-time Sensor Data, last 5 hours",
			xaxis: {min: ago, max: now},
			yaxis: {min: 20, max: 100,
					tickFormatter: function(val) {return val+"% RH";}},
			y2axis: {min: 15, max: 30,
					tickFormatter: function(val) {return val+" °C";}}
		}
	);
	
}