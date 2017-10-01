

$(document).ready(function(){
	//Logic to convert JSON to HTML table
	var strnotes = $('td.ingredient_notes_json');
    //console.log(strnotes);
    //console.log(jQuery.type(strnotes));
	
	$(strnotes).each(function(i, row) {
		var r = $(row);
		//console.log(row);

		var $this = $(row).text();
		//console.log(jQuery.type($this));
		var json = JSON.parse($this).pricing;
		//console.log(json);
		//console.log(jQuery.type(json));
		var tbl_body = document.createElement("table");
		var header = tbl_body.createTHead();
		var	footer = tbl_body.createTFoot();
		var	tfoot = footer.insertRow();
		var thead = header.insertRow();
		thead.className = 'tiny_thead';
		footer.className = 'tiny_tfoot';
		
		var trow = "<td>Unit</td><td>Type</td><td>Min</td><td>Max</td><td>Price</td><td>Frt. Type</td><td>FOB</td><td>Frt. Cost</td>";
		var frow = "<tr><td>Notes:</td><td colspan='7'>"+json.map(function(n){return n.notes;});+"</td></tr>";
		thead.innerHTML = trow;
		tfoot.innerHTML = frow;
		tbl_body.className = "tiny_table";
		// var odd_even = false;
        var transform = {
		  tag: 'tr',
		  children: [{
		    "tag": "td",
		    "html": "${unit_type}"
		  }, {
		    "tag": "td",
		    "html": "${packaging_type}"
		  }, {
		    "tag": "td",
		    "html": "${min_qty}"
		  }, {
		    "tag": "td",
		    "html": "${max_qty}"
		  }, {
		    "tag": "td",
		    "html": "${price}"
		  }, {
		    "tag": "td",
		    "html": "${freight_type}"
		  }, {
		    "tag": "td",
		    "html": "${fob_point}"
		  }, {
		    "tag": "td",
		    "html": "${freight_cost}"
		}]
		  
		};

		$(row).html(tbl_body);
        $(tbl_body).json2html(json, transform);
	});



//Makes table look pretty!
	$('.iuc_num').css('width', '3%');
	$('.ingredient').css('width', '6%');
	$('.supplier').css('width', '6%');
	$('.item_price').css('width', '3%');
	$('.item_price').css('text-align', 'right');
	$('.ext_price').css('width', '3%');
	$('.ext_price').css('text-align', 'right');
	$('.percentage').css('width', '3%');
	$('.percentage').css('text-align', 'right');
	$('.recipe_weight').css('width', '3%');
	$('.recipe_weight').css('text-align', 'right');
	$('.SPG').css('width', '3%');
	$('.SPG').css('text-align', 'right');
	$('.csm').css('width', '1%');
	$('.csm').css('text-align', 'right');
	$('.ingredient_notes_json').css('width', '15%');
	$('.tiny_table').attr('width', '100%');
	$('td.tiny_table').attr('text-align', 'center');
	$('.tiny_thead').css('text-align', 'center');
	//$('.tiny_tfoot').css('colspan', '6');
	//$('td.tiny_table').css('width', '%');
	$('.ingredient_notes_json').css('text-align', 'left');
	$('.customgray tfoot').css('text-align', 'right');


});