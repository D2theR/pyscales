
$(function() {
    $('#id_batch_adjust').bind('keyup', function(event) {
        var previousValue = parseFloat($(".field-batch_weight p").text());
        var newValue = parseFloat($(event.target).val());
        //console.log(previousValue, newValue);
        //var newPercent = parseFloat($(event.target).val());
        if (previousValue && newValue) {
            $('.ingredient-table > tbody > tr').each(function(tr, p) {
            	var percent = parseFloat($('#recipe-'+tr+' td.field-percentage p').text());
            	var boxValue = parseFloat($('input#id_recipe-'+tr+"-recipe_weight").val());
            	//console.log(tr, percent, boxValue);
            	var newIngredientVal = newValue * (percent / 100);
            	$('input#id_recipe-'+tr+"-recipe_weight").val(newIngredientVal.toFixed(3)); 				
 				
            });
            $('.field-box field-batch_weight p').val(newValue);
        }	
    });
});