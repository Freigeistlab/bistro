// connect to the websocket of our app
var ws = new WebSocket("ws://192.168.0.111:5678/");

// wait for messages incoming
ws.onmessage = function (event) {
	// convert the string we get into a JSON object
	var json = JSON.parse(event.data);
	var timeout = 0;

	// add items to waiting list
	var waiting = $("#waitingList span.item").length;
	var diff = waiting - json["waiting"];
	if (diff < 0) {
		for (var i = waiting; i < json["waiting"]; i++) {
			$("#waitingList").prepend("<span class='item new'></span");
			setTimeout(function() {
				$("#waitingList span.item.new").removeClass("new");
			}, 10);
		}
	} else if (diff > 0) {
		timeout = 250;
		for (var i = waiting; i > json["waiting"]; i--) {
			$($("#waitingList span.item")[i-1]).addClass("old");
			setTimeout(function() {
				$("#waitingList span.item.old").remove();
			}, 500);
		}
	}

	
	setTimeout(function() {
		// show name of current recipe
		document.getElementById("currentRecipe").innerText = json["recipe"];

		if (json["setup"] == 1) {
			$("#setup").css("display","block");
			$("#waiting").css("display","none");
			$("#current").css("display","none");
		} else {
			$("#setup").css("display","none");
			$("#waiting").css("display","block");
			$("#current").css("display","block");
		}

		$("#scales .circles span").removeClass("red").removeClass("yellow").removeClass("green");
		for (var i = 0; i < 13; i++){
			if (json["weight"] / 6.0 > i / 13.0) {
				var classToAdd = "green";
				if (i > 6) classToAdd = "yellow";
				if (i > 9) classToAdd = "red";
				$($("#scales .circles span")[12-i]).addClass(classToAdd);
			};
		}

		if (json["recipe"] == "") {
			$("td").removeClass("use").addClass("ready");
			$("#countdown").addClass("active");
		}

		// iterate through all our ingredients
		for (var ingredient in json.ingredients) {
			// each cell in the table of our HTML page gets its respective CSS class
			// that will cause it to show the right color (see bistro.css)
			// json[ingredient] contains one of the following: "success", "neutral", "blink", or "error"
			document.getElementById(ingredient).className = json.ingredients[ingredient];
			if (json.ingredients[ingredient] == "ready") {
				$("#countdown").addClass("active");
			} else {
				$("#countdown").removeClass("active")
			}
		}

		
		if (json["error"]) {
			$("#"+json["error"]).addClass("error");
			setTimeout(function() {
				$("#"+json["error"]).removeClass("error");
			}, 3600);
		}
	}, timeout);

	
};