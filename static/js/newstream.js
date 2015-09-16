
function addClickability() {
	$(".tweet-tile-interior").click(function(){
		$("#"+focused_thread).removeClass("active-thread");
		$(this).addClass("active-thread");
		focused_thread = $(this).attr('id');
		hashtag_to_track = $("#hashtagToTrack-js").text().trim();
		thought_hashtag = $(".sidebar-content-js").attr('id');
		full_hashtag_text = " #"+thought_hashtag + " #"+hashtag_to_track;
		$(".chars").text(140 - full_hashtag_text.length);
		focused_data = $.parseJSON($(this).children('input').val());
		$.ajax({
			  type: "POST",
			  contentType: "application/json; charset=utf-8",
			  url: "/focus",
			  data: JSON.stringify(focused_data)
			}).done(function(focusHtml){
				$('#sidebar-content-js').html(focusHtml);
			})
	});
}

$( document ).ready(function() {
	focused_thread = $(".tweet-tile-interior:first").attr('id');
	addClickability();
	
	$(".tweet-tile-interior:first").addClass("active-thread");
	window.setInterval(function(){
		$.get( "/refresh", function( tweetHtml ) {
			$("#tweetcard-js").html(tweetHtml);
			addClickability();
			$("#"+focused_thread).addClass("active-thread");
		});
		
	}, 5000);

	$("#new-thread-button").click(function(){
		$("#focusThread").toggle();
		$("#newThread").toggle();
		if ($("#new-group-name").is(':visible')==true) {
			new_thread = true;
			$("#"+ focused_thread).removeClass("thought-tile-selected");
			updateNumCharsAllowed(106); // ---- HA why 106?
		}
		else{
			new_thread = false;
			$("#"+ focused_thread).addClass("thought-tile-selected");
			var numCharsUsed = 140-(" #" + focused_thread + " #tfivefifty").length;
			updateNumCharsAllowed(numCharsUsed);
		}
	});
});




