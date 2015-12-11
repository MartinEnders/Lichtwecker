$(document).ready(function(){

    $( "<style type=\"text/css\">" +
       "button, input[type=time] { height: 5cm; font-size: 2.8cm; margin-bottom: 5px;} " +
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

    var time_form = $("<input type='time' value='' />");
    var set_time = $("<span></span>");

    $.get("/get_time",function(data){
	time_form.val(data);
	set_time.text(data);
    });


    var save_time = function(data){
	// set_time, weckzeit
	$.get("/set_time",
	      {'weckzeit': time_form.val()},
	      function(data){
		  set_time.text(data);
	      });
    };
    
    time_form.change(save_time);
	     
    
    on_button.click(function(evt){
	$.get("/light_on", function(data){console.log(data);});
    });

    off_button.click(function(evt){
	$.get("/light_off", function(data){console.log(data);});
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
	    

    
    $("#content")
	.append(on_button)
	.append(off_button)
	.append(time_form)
	.append(set_time)
	.append(wecker_on_off);


});
