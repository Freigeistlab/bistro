/*import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:5000"
});
*/

// on start check if server is up and running -- otherwise restart after 5 secs

async function pingServer(){

  const response = await fetch("http://localhost:5000/").catch((error) => {
    console.error('network error: ' + error);
    setTimeout(function(){
    window.location.reload();
    }, 10000);
  });
  if (response){
      if (response.status !== 200) {
        setTimeout(function(){
            window.location.reload();
            }, 10000);
      } else {
        stopDemo();
      }
  }
}

setInterval(pingServer, 3000);




// connect to the websocket of our app
var ws = new WebSocket("ws://localhost:5678/");


var interval;
var demoStart;
var letterTimeouts = [];

const ingredientImages = {
  "Tomaten": "../../images/ingredients/Basilikum.jpg",
  "Hackfleisch": "../../images/ingredients/Kuh.jpg",
  "Chili": "../../images/ingredients/Chili.jpg",
  "Basilikum": "../../images/ingredients/Basilikum.jpg",
  "Knoblauch": "../../images/ingredients/Knoblauch.jpg",
  "KäseMix": "../../images/ingredients/Kaese.jpg",
  "marinierteKraeuter": "../../images/ingredients/Kraeuter.jpg",
  "Zwiebeln": "../../images/ingredients/Zwiebel.jpg",
  "gehacktePetersilie": "../../images/ingredients/Petersilie.jpg",
  "Sonnenblumenkerne": "../../images/ingredients/Sonnenblume.jpg",
  "getrockneteTomaten": "../../images/ingredients/GetrockneteTomaten.jpg",
  "Salbeibutter": "../../images/ingredients/Salbei.jpg",
  "Gorgonzola": "../../images/ingredients/Gorgonzola.jpg",
  "Speck": "../../images/ingredients/Schwein.jpg",
  "Rucola": "../../images/ingredients/Rucola.jpg",
  "Olivenoel": "../../images/ingredients/Olivenoel.jpg",
  "Bulgur": "../../images/ingredients/Bulgur.jpg",
  "Basilikumbutter": "../../images/ingredients/Basilikum.jpg",
};

function stopDemo(){
    $("#demo").empty();
}


function demo() {
  if ($(".waiting").length > 0 || $(".use").length > 0)
    return;

  interval = setInterval(function() {
    var current = $($("td")[Math.floor(Math.random() * 20)]);
    current.addClass("show");
    setTimeout(function(){
      current.removeClass("show");
    },5000)


    for (var l = 0; l < letterTimeouts.length;l++) {
      clearTimeout(letterTimeouts[l]);
    }
    letterTimeouts = [];
    if ($(".letter").length < 105) {
      var ingredient = ".";
      for (var l = 0; l < ingredient.length; l++) {
        letterTimeouts.push(setTimeout(function(ingredient,l) {
          var newLetter = $('<span class="letter" data-delay='+l+' data-letter="'+ingredient[l]+'">'+ingredient[l]+'</span>');
          newLetter.css("animation-delay", -20+0.5*l+"s");
          $("#demo").append(newLetter);
        },l * 100, ingredient, l));
      }
    }

  }, 100);
}
$(document).ready(function() {
  demo();
});

function drawBackgroundAnimation(json, diff){
  // iterate through all our ingredients
  console.log("drawing bg animation", json);
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
      $("#demo").empty();
      $("#currentIngredient").empty();

      console.log("adding ingredients ");

      let imageSrc = ingredientImages[ingredient];

      let image = $('<img id="img1" class="ingredientImage" src="' + imageSrc + '" alt="Ingredient">');
      let ingredientText = $('<span class="ingredientText" >'+ingredient+'</span>').css({animationDuration: "10s", top: 100});
      let image1 = $('<img id="img3" class="ingredientImage" src="' + imageSrc + '" alt="Ingredient">').css({animationDuration: "8s", top: 200});
      let ingredientText1 = $('<span class="ingredientText" >'+ingredient+'</span>').css({animationDuration: "6s", top: 300})
      let image2 = $('<img id="img3" class="ingredientImage" src="' + imageSrc + '"  alt="Ingredient">').css({animationDuration: "11s", top: 400});
      let ingredientText2 = $('<span class="ingredientText" >'+ingredient+'</span>').css({animationDuration: "5s", top: 500})

      $("#currentIngredient").append(image);
      $("#currentIngredient").append(image1);
      $("#currentIngredient").append(image2);
      $("#currentIngredient").append(ingredientText);
      $("#currentIngredient").append(ingredientText1);
      $("#currentIngredient").append(ingredientText2);


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
      for (var l = 0; l < letterTimeouts.length;l++) {
        clearTimeout(letterTimeouts[l]);
      }
      letterTimeouts = [];
      $("#demo").empty();
    } else {
      $("#countdown").removeClass("active")
    }
  }

}

function updateWaitingList(diff, waiting){
  if (diff > 0) {
    for (var i = 0; i < diff; i++) {
      $("#waitingList").prepend("<span class='item new'/>");
      setTimeout(function() {
        $("#waitingList span.item.new").removeClass("new");
      }, 10);
    }
  } else if (diff < 0) {
    timeout = 250;
    for (var i = waiting; i > waiting + diff; i--) {
      $($("#waitingList span.item")[i-1]).addClass("old");
      setTimeout(function() {
        $("#waitingList span.item.old").remove();
      }, 500);
    }
  }
}

// wait for messages incoming
ws.onmessage = function (event) {
  clearInterval(interval);
  clearTimeout(demoStart);
// convert the string we get into a JSON object
  console.log("new message received")
  
  console.log(event.data)
  var json = JSON.parse(event.data);
  
  switch(json.action){
    case "restart":
      setTimeout(function() {
        window.location.reload();
      }, 5000);
      break;
    case "refresh":
      console.log("Refreshing")
      window.location.reload();
      break;
    case "new_order":
      var waiting = $("#waitingList span.item").length;
      updateWaitingList(1, waiting);
      return;
    case "clear_queue":
      var waiting = $("#waitingList span.item").length;
      updateWaitingList(-waiting, waiting);
      return;
    default:
      break;
  }

  console.log(json)
  let timeout = 0;

// add items to waiting list
  waiting = $("#waitingList span.item").length;
  const diff = json["waiting"] - waiting;
  updateWaitingList(diff, waiting)



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

    drawBackgroundAnimation(json, diff);

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
