getGraphData = function() {

	var xhr = new XMLHttpRequest();
	var data;
	
	xhr.open('GET', 'data.html');
	xhr.send(null);

	xhr.onreadystatechange = function () {
		var DONE = 4; // readyState 4 means the request is done.
		var OK = 200; // status 200 is a successful return.
		if (xhr.readyState === DONE) {
			if (xhr.status === OK) {
				//console.log(xhr.responseText);
				data = JSON.parse(xhr.responseText);
				plotData(data);
			} else {
			    console.log('Error: ' + xhr.status); // An error occurred during the request.
			}
		}
	};

}

setInterval(getGraphData, 5000)
getGraphData()