$(document).ready(function(){

    $( "<style type=\"text/css\">" +
       "button, input[type=time], input[type=number] { height: 5cm; font-size: 2.8cm; margin-bottom: 5px;} " +
       "button { width: 100%; } " +
       "input[type=checkbox] { " + 
       "  zoom : 8; " + 
       "  margin: 10px;} "+
       "body { } " +
       "span {font-size: 2.8cm; font-weight: bold;} " +
       "</style>")
	.appendTo( "head" );

    var on_button = $("<button>On</button>");
    var off_button = $("<button>Off</button>");
    var shutdown_button = $("<button>Shutdown</button>");

    var time_form = $("<input type='time' value='' />");
    var set_time = $("<span></span>");
    var time_to_wake_up = $("<div></div>");
    var light_start = $("<div></div>");

    var dimm_zeit_label = $("<span>Dimmdauer</span>");
    var nachleuchten_label = $("<span>Nachleuchten</span>");
    var dimm_zeit = $("<input type='number' min='1' max='120' /><br />");
    var nachleuchten = $("<input type='number' min='1' max='120' /><br />");

    time_to_wake_up.css("font-size", '2.8cm');
    light_start.css("font-size", "0.5cm");

    var init_weckzeit_form = function(data){
	form_value = data.split(";")[0];
	wake_up_value = data.split(";")[1];
	l_start =  data.split(";")[2];
	time_form.val(form_value);
	set_time.text(form_value);
	time_to_wake_up.text("Schlafzeit: " + wake_up_value);
	light_start.text("Lichtstart: " + l_start);
    };
    
    $.get("/get_time",init_weckzeit_form);


    var save_time = function(data){
	// set_time, weckzeit
	$.get("/set_time",
	      {'weckzeit': time_form.val()},
	      init_weckzeit_form);
    };
    
    time_form.change(save_time);
	     
    
    on_button.click(function(evt){
	$.get("/light_on", function(data){console.log(data);});
    });

    off_button.click(function(evt){
	$.get("/light_off", function(data){console.log(data);});
    });

    shutdown_button.click(function(evt){
	$.get("/shutdown_pi", function(data){console.log(data);});
    });


    // Checkbox
    // set_wecken_p,  wecken_p
    var wecker_on_off = $("<input type=checkbox class='check' />");

    $.get("/get_wecken_p", function(data){
	if(data == 'on'){
	    wecker_on_off.prop( "checked", true );
	}else if(data=='off'){
	    wecker_on_off.prop( "checked", false );
	}
    });

    wecker_on_off.change(function(evt){
	var status = (wecker_on_off.prop( "checked" ) ? 'on' : 'off');
	$.get("/set_wecken_p",
	      {'wecken_p' : status},
	      function(data){
		  if(data == 'error'){
		      alert('fehler');
		  }
	      });

    });


    //dimm_zeit

    $.get("/get_dimmdauer",
	  function(data){
	      dimm_zeit.val(data);
	  });
    
    dimm_zeit.change(function(evt){
	$.get("/set_dimmdauer",
	      {"dimmdauer" : dimm_zeit.val()},
	      function(data){
		  dimmdauer = data.split(";")[0]
		  startzeit = data.split(";")[1]
		  dimm_zeit.val(dimmdauer);
		  light_start.text("Lichtstart: " + startzeit);
		  dimm_zeit_label.fadeOut(400,function(){dimm_zeit_label.fadeIn(400);});

	      });
    });

    //nachleuchten
    $.get("/get_nachleuchten",
	  function(data){
	      nachleuchten.val(data);
	  });
    
    nachleuchten.change(function(evt){
	$.get("/set_nachleuchten",
	      {"nachleuchten" : nachleuchten.val()},
	      function(data){
		  nachleuchten.val(data);
		  nachleuchten_label.fadeOut(400,function(){nachleuchten_label.fadeIn(400);});
	      });
    });

    
    
    $("#content")
	.append(on_button)
	.append(off_button)
	.append(time_form)
	.append(set_time)
	.append(wecker_on_off)
	.append(time_to_wake_up)
	.append(light_start)
	.append(dimm_zeit_label)
	.append(dimm_zeit)
	.append(nachleuchten_label)
	.append(nachleuchten)
        .append(shutdown_button);

});
