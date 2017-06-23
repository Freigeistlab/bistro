var ws = new WebSocket("ws://localhost:5678/");
ws.onmessage = function (event) {
	console.log(event.data);
	var json = JSON.parse(event.data)
	for (var ingredient in json) {
		document.getElementById(ingredient).className = json[ingredient];
	}
};