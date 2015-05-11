$( document ).ready(function() {
	window.setInterval(function(){
		$.get( "/stream", function( data ) {
			// console.log(data);
		});
	}, 5000);
	$(".thought-tile").click(function(){
		hashtag = $(this).attr('id');
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
	});
	$("#sort-my-thoughts-button").click(function(){
		$(".tweet-tile").each(function(index){
			console.log($(this));
			// console.log($(this).text());
		});
	})
});