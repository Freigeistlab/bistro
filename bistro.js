// connect to the websocket of our app
var ws = new WebSocket("ws://192.168.1.15:5678/");

// wait for messages incoming
ws.onmessage = function (event) {
	// convert the string we get into a JSON object
	var json = JSON.parse(event.data)

	// iterate through all our ingredients
	for (var ingredient in json) {
		// each cell in the table of our HTML page gets its respective CSS class
		// that will cause it to show the right color (see bistro.css)
		// json[ingredient] contains one of the following: "success", "neutral", "blink", or "error"
		document.getElementById(ingredient).className = json[ingredient];
	}
};