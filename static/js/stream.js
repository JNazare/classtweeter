$( document ).ready(function() {
	window.setInterval(function(){
		$.get( "/stream", function( data ) {
			console.log(data);
		});
	}, 5000);
});