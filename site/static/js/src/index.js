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
// Refill Form
//      On reloads and navigation without submission, we want to
//      set the form values to the sessionStorage saved values
//      so that they don't lose their options.
window.addEventListener('load',function(){
    var elements = document.forms[0].elements;
    for( var i = 0; i < elements.length; i++ ){
        var obj = elements[i];
        if(obj.type=='checkbox'){
            if(obj.name in sessionStorage){
                obj.checked = (sessionStorage[obj.name]!="false");
            }
        }
        else if(['text','number','select-one'].indexOf(obj.type) >= 0){
            if(obj.name in sessionStorage){
                if(obj.type=="number"){
                    obj.value = parseInt(sessionStorage[obj.name]);
                } else {
                    obj.value = sessionStorage[obj.name];
                }
            }
        }
    }
})

// -----------------------------------------------------------------------------
// Localize the datetime on title-cards
var dates = document.getElementsByClassName('js-localize-date');
for( var i = 0; i < dates.length; i++ ){
    var block = dates[i]
    var date = new Date( block.getAttribute('iso') );
    block.innerHTML = date.toLocaleDateString() + " " + date.toLocaleTimeString();
}

// -----------------------------------------------------------------------------
//	Layout:
// 		rather than search for elements in each function/handler
// 		this layout object gets the searching out of the way up
// 		front.
layout = {
	all:document.getElementById('all-check'),
	form:document.getElementById('js-sidebar-form'),
	search:document.getElementById('js-search-input'),
	number:document.getElementById('js-number-input'),
	category:document.getElementById('js-category-select'),
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
        sessionStorage[this.name] = this.checked;
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
        sessionStorage[layout.all.name] = layout.all.checked;
	});
}

// -----------------------------------------------------------------------------
// Save Changes (search,number,category)
//      sessionStorage values are saved for checkboxes in
//      the other handlers, but we didn't have handlers
//      for these inputs, so these were added.
layout.search.addEventListener('change',function(_event){
    sessionStorage[this.name] = this.value;
});

layout.number.addEventListener('change',function(_event){
    sessionStorage[this.name] = this.value;
});

layout.category.addEventListener('change',function(_event){
    sessionStorage[this.name] = this.value;
});

// -----------------------------------------------------------------------------
// All:
// 		on 'all' change, select/unselect all sources
layout.all.addEventListener('change',function(_event){
	var caller = this;
	layout.sources.forEach(function(source){
		source.checked = caller.checked;
        sessionStorage[source.name] = source.checked;
	});
    sessionStorage[this.name] = this.checked;
});

// -----------------------------------------------------------------------------
// Form:
// 		on form submit, preprocess data
layout.form.addEventListener('submit',function(_event){

});
