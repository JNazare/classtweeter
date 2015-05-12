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
			tweet_html = "<span>" + data.tweets[i].created_at_str + "</span>&nbsp;&nbsp;" + data.tweets[i].text;
			if(data.tweets[i].is_question){
				tweet_html =  '<span style="background-color: #E0F8E0">' + "<span>" + data.tweets[i].created_at_str + "</span>&nbsp;&nbsp;" + data.tweets[i].text  + '</span>'
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
		if ($("#new-group-name").is(':visible')==true) {
			$("#focusThread").toggle();
			$("#newThread").toggle();
		}
		sidebar = $('#sidebar');
		sidebar.scrollTop(sidebar.prop("scrollHeight"));
		focused_thread = hashtag;
	})
}

$( document ).ready(function() {
	show_only_my_tweets = false;
	focused_thread = $(".thought-tile:first").attr('id');
	new_thread = false;
	$("#"+focused_thread).addClass("thought-tile-selected")
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
				if(new_thread == false){
					$("#"+focused_thread).addClass("thought-tile-selected");
					focusThread(focused_thread);
				}
				if(show_only_my_tweets==true){
					showOnlyMyTweets();
				}
				$(".thought-tile").click(function(){
					$(".thought-tile").each(function(index){
						$(this).removeClass("thought-tile-selected")
					})
					$(this).addClass("thought-tile-selected");
					hashtag = $(this).attr('id');
					focusThread(hashtag);
				});
				console.log("refreshed tweets");
			});
		});
	}, 5000);

	$(".thought-tile").click(function(){
		$(".thought-tile").each(function(index){
			$(this).removeClass("thought-tile-selected")
		})
		$(this).addClass("thought-tile-selected");
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
		if ($("#new-group-name").is(':visible')==true) {
			new_thread = true;
			$("#"+ focused_thread).removeClass("thought-tile-selected");
		}
		else{
			new_thread = false;
			$("#"+ focused_thread).addClass("thought-tile-selected");
		}
	});
	$('#tweet-textarea').bind('input propertychange', function() {
		numCharsTotal = parseInt($('#charsTotal').text())
		numCharsInput = $('#tweet-textarea').val().length;
		$('#charsLeft').text((numCharsTotal - numCharsInput).toString())
	})
	$("#send-tweet-button").click(function(){
		text = $('#tweet-textarea').val();
		if (text.length > 0){
			additional_hashtags = $("#hashtag_to_add").val()
			if ($("#new-group-name").is(':visible')==true) {
				additional_hashtags = " #" + $("#new-group-name").val().toLowerCase().replace(" ", "_") + " #classtweeter";
			}
			composed_tweet = text + additional_hashtags;
			$.post( "/sendToTwitter", composed_tweet, function(data){
				$('#tweet-textarea').val("");
				$("#sent-alert").show();
				$("#new-thread-form-group").removeClass("has-error");
				$("#new-thread-control-label").text("New Thread Name");
				setTimeout(function() { $("#sent-alert").hide(); }, 3000)
			})
		}
		else{
			$("#new-thread-form-group").addClass("has-error");
			$("#new-thread-control-label").text("You must name the thread...");
		}
		
	})
});