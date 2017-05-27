// -----------------------------------------------------------------------------
// implement forEach if we're in IE -.-
if (!NodeList.prototype.forEach) {
    NodeList.prototype.forEach = function(fn, scope) {
        for(var i = 0, len = this.length; i < len; ++i) {
            fn.call(scope, this[i], i, this);
        }
    }
}


// -----------------------------------------------------------------------------
// Footer:
//		set the year on load
var today = new Date();
document.getElementById('js-footer-year').innerHTML = today.getFullYear();


// -----------------------------------------------------------------------------
//	Layout:
// 		rather than search for elements in each function/handler
// 		this layout object gets the searching out of the way up
// 		front.
layout = {
	all:document.getElementById('all-check'),
	plain:document.getElementById('plain-check'),
	regex:document.getElementById('regex-check'),
	form:document.getElementById('js-sidebar-form'),
	sources:document.querySelectorAll('.sources input:not(#all-check)'),
}

// -----------------------------------------------------------------------------
// Checkboxes:
//		if javascript is enabled, we grab all the checkboxes in the page,
//		hide them and apply a class that displays an alternate 'checkbox'
var inputs = document.querySelectorAll('input[type=checkbox]');
for( var i = 0; i < inputs.length; i++ ){
	inputs[i].style.display = "none";
	inputs[i].classList.add('checkable');
}

// -----------------------------------------------------------------------------
// Sources:
// 		on changing source options, unselect/select 'all' appropriately
for( var i = 0; i < layout.sources.length; i++ ){
	layout.sources[i].addEventListener('change',function(_event){
		if(this.checked){
			layout.all.checked = true;
			layout.sources.forEach(function(source){
				if(!source.checked){
					layout.all.checked = false;
				}
			});
		} else {
			layout.all.checked = false;
		}
	});
}

// -----------------------------------------------------------------------------
// Regex/Plain:
// 		on 'regex' and 'plain', alternate checks (only one gets submitted)
layout.plain.addEventListener('change',function(_event){
	layout.regex.checked = !this.checked;
});

layout.regex.addEventListener('change',function(_event){
	layout.plain.checked = !this.checked;
});

// -----------------------------------------------------------------------------
// All:
// 		on 'all' change, select/unselect all sources
layout.all.addEventListener('change',function(_event){
	var caller = this;
	layout.sources.forEach(function(source){
		source.checked = caller.checked;
	});
});

// -----------------------------------------------------------------------------
// Form:
// 		on form submit, preprocess data
layout.form.addEventListener('submit',function(_event){
	layout.plain = !layout.regex;												// sanity check
	if(layout.all.checked){														// if 'all' submit only that, otherwise individual checks
		layout.sources.forEach(function(source){
			source.checked = false;
		});
	}
});
