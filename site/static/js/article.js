// -----------------------------------------------------------------------------
// LAYOUT ELEMENTS
// -----------------------------------------------------------------------------

layout = {
	// article DOM elements
	notification: document.querySelector('#notification'),
	annotation: document.querySelector('#annotation'),


	article: document.querySelector('#article'),
	title: document.querySelector('#title'),
	author: document.querySelector('#author'),
	publish_date: document.querySelector('#publish_date'),
	content: document.querySelector('#content'),
	people: document.querySelector('#people'),
	id: document.querySelector('#id'),
	source: document.querySelector('#source'),
	link: document.querySelector('#link'),
}

// -----------------------------------------------------------------------------
// GLOBAL VARIABLES
// -----------------------------------------------------------------------------
globals = {
	// a list of names for the current article
	people: null,

	// primary key of current article
	pk: layout.article.getAttribute('pk'),

	// a summary of the current selection (annotation)
	summary: null,

	// a global to track the last highlighted text
	capture:null,
}

// -----------------------------------------------------------------------------
// HANDLERS: either response or to events
// -----------------------------------------------------------------------------
function refresh_handler( response ){
	var people_html = '';

	globals.people = response.people.split(';').filter(function(entry) { return entry.trim() != ''; });
	for( var i=0; i<globals.people.length; i++){
		people_html += '<span class="name">' + globals.people[i].trim() + '<x-remove onmousedown="remove_handler( this )">&minus;</x-remove></span>';
	}

	layout.content.innerHTML = response.content;
}

function select_handler( _event ) {
	if( typeof(window.getSelection) != "undefined" ){
		var selection = window.getSelection();
		var range = selection.getRangeAt(0);

		if( selection.rangeCount > 0 && !range.collapsed ) {
			var text = range.toString();
			if(text.length<50){
				layout.notification.innerHTML='Add "' + text + '" as an annotation?<br/><span onClick="add_handler(\'' + text + '\');clear_notification();">Yes</span> <span onClick="clear_notification();">No</span>';
				layout.notification.style.visibility = 'visible';
			}
		}
	}
}

function clear_notification(){
	layout.notification.innerHTML = '';
	layout.notification.style.visibility = 'hidden';
}

function add_handler( name ){
	if(globals.people!=null){
		if (globals.people.indexOf(name)<0){
			globals.people.push(name);
			layout.people.innerHTML += '<span class="name">' + name + '<x-remove onmousedown="remove_handler( this )">&minus;</x-remove></span>';
			refresh_requestor();
		}
	}
}

function remove_handler( element ){
	if(globals.people!=null){
		var parent = element.parentNode;
		var gparent = parent.parentNode;

		if(parent!=null&&gparent!=null){
			parent.removeChild(element);
			var name = parent.textContent;

			gparent.removeChild(parent);

			var index = globals.people.indexOf(name);
			if( index >= 0 ){
				globals.people.splice( index, 1 );
				refresh_requestor();
			}
		}
	}
}

function summary_handler( response ){
	layout.annotation.innerHTML = response.summary;
	globals.annotation_open = true;
}

// -----------------------------------------------------------------------------
// REQUESTORS: of endpoints
// -----------------------------------------------------------------------------
function refresh_requestor(){
	if(globals.pk!=null){
		var people_str = globals.people.join(';');
		network.post('refresh', { pk:globals.pk, people:people_str })
	}
}

function summary_requestor( element ){
	var name = element.getAttribute('name');

	layout.annotation.innerHTML = '<div class="loader"></div>';
	layout.annotation.style.visibility = 'visible';
	network.get('annotations',{ name:name })
}

// -----------------------------------------------------------------------------
// LISTENER DECLARATIONS
// -----------------------------------------------------------------------------
layout.content.addEventListener('mouseup',select_handler);


network.register('refresh', refresh_handler);
network.register('annotations', summary_handler);



refresh_requestor();
