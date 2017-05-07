$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				message : $('#message').val(),
				media : $('#media').val()
			},
			type : 'POST',
			url : '/put_message'
		})
		.done(function(data) {
            $("input[type=text], textarea").val("");

            console.log(data.name);
            var text = data.name['text'];
            var image = data.name['media'];
            var date = data.name['date'][0];
            var time = data.name['time'][0];


			if (data.error) {
				$('#errorAlert').text(data.error).show();
				$('#successAlert').hide();
			}
			else {
				//$('#successAlert').text(data.name['text']).show();
				$('#new_msg').prepend("<li><h3>"+text+"</h3></li><img scr="+image+">"+date+" | "+time+"</li>").show();

			}

		});

		event.preventDefault();

	});


});