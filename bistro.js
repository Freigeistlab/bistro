// connect to the websocket of our app
var ws = new WebSocket("ws://192.168.0.111:5678/");


var interval;
var demoStart;
function demo() {
	if ($(".waiting").length > 0 || $(".use").length > 0)
		return;
	
	interval = setInterval(function() {
		var current = $($("td")[Math.floor(Math.random() * 20)]);
		current.addClass("show");
		setTimeout(function(){
			current.removeClass("show");
		},5000)

		
		if ($(".letter").length < 28) {
			var ingredient = ".";
			for (var l = 0; l < ingredient.length; l++) {
				setTimeout(function(ingredient,l) {
					var newLetter = $('<span class="letter" data-delay='+l+' data-letter="'+ingredient[l]+'">'+ingredient[l]+'</span>');
					newLetter.css("animation-delay", -20+0.5*l+"s");
					$("#currentIngredient").append(newLetter);
				},l * 100, ingredient, l);
			}
		}

	}, 100);
}

$(document).ready(function() {
	demo();
});

// wait for messages incoming
ws.onmessage = function (event) {
	clearInterval(interval);
	clearTimeout(demoStart);
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
		var currentRecipe = document.getElementById("currentRecipe");
		if (currentRecipe)
			currentRecipe.innerText = json["recipe"];

		var extras = document.getElementById("extras");
		if (extras)
			extras.innerText = json["extras"];

		var preparation = document.getElementById("preparation");
		if (preparation)
			preparation.innerText = json["preparation"];

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
			clearTimeout($(".error").data("errorTimeout"));
			$(".error").removeClass("error");
			demoStart = setTimeout(function() {
				$("td").removeClass("ready");
				demo();	
				$("#countdown").removeClass("active");
			}, 6000);
			
		}

		// iterate through all our ingredients
		for (var ingredient in json.ingredients) {
			// each cell in the table of our HTML page gets its respective CSS class
			// that will cause it to show the right color (see bistro.css)
			// json[ingredient] contains one of the following: "success", "neutral", "blink", or "error"
			if ($("#"+ingredient).hasClass("error")) {
				var element = document.getElementById(ingredient.replace(" ","_"));
				if (element)
					element.className = json.ingredients[ingredient] + " error";
			} else if (json.ingredients[ingredient] == "use") {
				var use = document.getElementById(ingredient);
				$("#currentIngredient").empty();
				for (var l = 0; l < ingredient.length; l++) {
					setTimeout(function(ingredient,l) {
						var newLetter = $('<span class="letter" data-delay='+l+' data-letter="'+ingredient[l]+'">'+ingredient[l]+'</span>');
						newLetter.css("animation-delay", -20+0.5*l+"s");
						$("#currentIngredient").append(newLetter);
					},l * 100, ingredient, l);
				}
				
				if (diff < 0) {
					if (use) {
						use.className = "use";
					}
				} else {
					if (use) {
						use.className = "waiting toUse";
						setTimeout(function() {
							$(".toUse").removeClass("waiting").removeClass("toUse").addClass("use");
						},1000);
					}
				}
			} else {
				var element = document.getElementById(ingredient.replace(" ","_"));
				if (element)
					element.className = json.ingredients[ingredient];
			}
			
			if (json.ingredients[ingredient] == "ready") {
				$("#countdown").addClass("active");
				$("#currentIngredient").empty();
			} else {
				$("#countdown").removeClass("active")
			}
		}

		
		if (json["error"]) {
			$("#"+json["error"]).removeClass("error");
			clearTimeout($("#"+json["error"]).data("errorTimeout"));

			$("#"+json["error"]).addClass("error");
			var t = setTimeout(function() {
				$("#"+json["error"]).removeClass("error");
			}, 3600);
			$("#"+json["error"]).data("errorTimeout", t);
		}
	}, timeout);

	
};