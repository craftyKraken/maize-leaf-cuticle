getStatusData = function() {

	var xhr = new XMLHttpRequest();
	var data;
	
	xhr.open('GET', 'status.html');
	xhr.send(null);

	xhr.onreadystatechange = function () {
		var DONE = 4; // readyState 4 means the request is done.
		var OK = 200; // status 200 is a successful return.
		if (xhr.readyState === DONE) {
			if (xhr.status === OK) {
				//console.log(xhr.responseText);
				data = JSON.parse(xhr.responseText);
				document.getElementById('status').innerHTML = data[0].toString();
				document.getElementById('timeCode').innerHTML = data[1].toString();
				var time = data[2]
				
				document.getElementById('time').innerHTML = data[2].toString();
			} else {
			    console.log('Error: ' + xhr.status); // An error occurred during the request.
			}
		}
	};

}

setInterval(getStatusData, 1000)
getStatusData()