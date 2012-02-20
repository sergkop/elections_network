(function($){
	$(function(){
		$('.verification_td button').click(function(){
			var td = $($(this).parents('.verification_td')[0]);
			var form = $(td.find('form'))
			$.post(form.attr('action'), form.serialize(), function(data){
				if (data == 'ok'){
					$(td.parents('tr')[0]).hide();
				}else{
					alert(data);
				}
			})
		});
	});
})(jQuery);
