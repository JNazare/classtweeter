function showOnlyMyTweets(){
	$(".tweet-tile").each(function(index){
		author_class = $(this).attr('class').split(" ")[0];
		if(author_class == "author_false"){
			$(this).hide();
		}
	});
	show_only_my_tweets = true
}

function showAllTweets(){
	$(".tweet-tile").each(function(index){
		$(this).show();
	});
	show_only_my_tweets = false
}

function focusThread(hashtag){
	$.post( "/contentsOfHashtag", {"hashtag": hashtag}, function(data){
		$('#focused-group-name').text(data.groupName);
		html_string=""
		for(i=data.tweets.length-1; i>-1; i--){
			tweet_html = data.tweets[i].text;
			if(data.tweets[i].is_question){
				tweet_html =  '<span style="background-color: #E0F8E0">' + data.tweets[i].text  + '</span>'
			}
			html_string = html_string + "<p>" + tweet_html +"</p>"
		}
		$("#focused-group-tweets").html(html_string);
		img_html = ''
		img_html_1 = '<img src="'
		img_html_2 = '" class="img-circle" style="height:30px; width:30px; float:right; margin-top: -5px; margin-right: 2px; margin-left: 2px;" alt="Circular Image">'
		num_avatars = data.user_photos.length;
		if(num_avatars>3){
			num_avatars=3;
			$("#focused-more-avatars").text(String(data.user_photos.length-3)+"+");
			$("#focused-more-avatars").parent().show();
		}
		else{
			$("#focused-more-avatars").parent().hide();
		}
		for(i=0; i<num_avatars; i++){
			img_html = img_html + img_html_1 + data.user_photos[i] + img_html_2
		}
		$('#focused-group-avatars').html(img_html)
	})
}

$( document ).ready(function() {
	show_only_my_tweets = false
	window.setInterval(function(){
		$.get( "/stream", function( data ) {
			data = $.parseJSON(data);
			$.ajax({
			  type: "POST",
			  contentType: "application/json; charset=utf-8",
			  url: "/getTweetTile",
			  data: JSON.stringify(data)
			}).done(function(tweet_html){
				$("#allTweets").html(tweet_html);
				if(show_only_my_tweets==true){
					showOnlyMyTweets();
				}
				$(".thought-tile").click(function(){
					hashtag = $(this).attr('id');
					focusThread(hashtag);
				});
				console.log("refreshed tweets");
			});
		});
	}, 5000);

	$(".thought-tile").click(function(){
		hashtag = $(this).attr('id');
		focusThread(hashtag);
	});

	$("#sort-my-thoughts-button").click(function(){
		showOnlyMyTweets()
	});
	$("#sort-most-recent-button").click(function(){
		showAllTweets()
	});
	$("#new-thread-button").click(function(){
		$("#focusThread").toggle();
		$("#newThread").toggle();
	});
	$('#tweet-textarea').bind('input propertychange', function() {
		numCharsTotal = parseInt($('#charsTotal').text())
		numCharsInput = $('#tweet-textarea').val().length;
		$('#charsLeft').text((numCharsTotal - numCharsInput).toString())
	})
	$("#send-tweet-button").click(function(){
		text = $('#tweet-textarea').val();
		additional_hashtags = $("#hashtag_to_add").val()
		if ($("#new-group-name").is(':visible')==true) {
			additional_hashtags = " #" + $("#new-group-name").val().toLowerCase().replace(" ", "_") + " #classtweeter";
		}
		composed_tweet = text + additional_hashtags;
		$.post( "/sendToTwitter", composed_tweet, function(data){
			$('#tweet-textarea').val("");
			$("#sent-alert").show();
			setTimeout(function() { $("#sent-alert").hide(); }, 3000)
		})
	})
});