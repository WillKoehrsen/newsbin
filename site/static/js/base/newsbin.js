// -----------------------------------------------------------------------------
// LAYOUT ELEMENTS
// -----------------------------------------------------------------------------

var example_summary = window.document.createElement('div');


layout = {
	// top DOM elements
	all_check: document.querySelector('#all_check'),
	reg_check: document.querySelector('#reg_check'),
	pla_check: document.querySelector('#pla_check'),
	sources: document.querySelector('#sources'),

	// right-side DOM elements
	article: document.querySelector('#article'),
	title: document.querySelector('#title'),
	author: document.querySelector('#author'),
	publish_date: document.querySelector('#publish_date'),
	content: document.querySelector('#content'),
	people: document.querySelector('#people'),
	id: document.querySelector('#id'),
	source: document.querySelector('#source'),
	link: document.querySelector('#link'),

	// left-side DOM elements
	titles: document.querySelectorAll('.title'),
}

// -----------------------------------------------------------------------------
// GLOBAL VARIABLES
// -----------------------------------------------------------------------------
globals = {
	// a list of names for the current article
	people: null,

	// primary key of current article
	pk: null,

	// a summary of the current selection (annotation)
	summary: null,

	// a global to track the last highlighted text
	capture:null,

	// a global to track the last highlighted title
	title:null,

	// article starting position
	start: parseInt(window.getComputedStyle(layout.article).marginTop),
}

// -----------------------------------------------------------------------------
// HANDLERS: either response or to events
// -----------------------------------------------------------------------------
function load_handler( response ){

	// build the html for the people list at the bottom
	// of the article
	var people_html = '';
	globals.people = response.people.split(';').filter(function(entry) { return entry.trim() != ''; });
	for( var i=0; i<globals.people.length; i++){
		people_html += '<span class="name">' + globals.people[i].trim() + '<x-remove onmousedown="remove_handler( this )">&minus;</x-remove></span>';
	}

	// fill all the parts of the article with the
	// appropriate values
	layout.title.innerHTML = response.title;
	layout.author.innerHTML = 'AUTHOR: ' + response.author;
	layout.publish_date.innerHTML = 'PUBLISHED: ' + response.publish_date;
	layout.content.innerHTML = response.content;
	layout.people.innerHTML = people_html;
	layout.id.innerHTML = 'ID: ' + response.id;
	layout.source.innerHTML = 'SOURCE: ' + response.source;
	layout.link.innerHTML = 'ORIGINAL: <a href="' + response.link + '">link</a>';
}

function refresh_handler( response ){
	var people_html = '';

	globals.people = response.people.split(';').filter(function(entry) { return entry.trim() != ''; });
	for( var i=0; i<globals.people.length; i++){
		people_html += '<span class="name">' + globals.people[i].trim() + '<x-remove onmousedown="remove_handler( this )">&minus;</x-remove></span>';
	}

	layout.content.innerHTML = response.content;
}

function scroll_handler(){
	var top = layout.article.getBoundingClientRect().top;
	var old_margin = parseInt(window.getComputedStyle(layout.article).marginTop);
	var new_margin = (-top)+old_margin;

	if(new_margin<globals.start){
		layout.article.style.marginTop = globals.start + 'px';
	} else {
		layout.article.style.marginTop = new_margin + 'px';
	}
}

function select_handler( _event ) {
	if( typeof(window.getSelection) != "undefined" ){
		var selection = window.getSelection();
		var range = selection.getRangeAt(0);

		if( selection.rangeCount > 0 && !range.collapsed ) {
			var text = range.toString();
			if(text.length<50){
				var notice = document.getElementById('notification');
				notice.innerHTML='Add "' + text + '" as an annotation? <span onClick="add_handler(\'' + text + '\');clear_notification();">Yes</span> <span onClick="clear_notification();">No</span>';
			}
		}
	}
}

function clear_notification(){
	document.getElementById('notification').innerHTML = '';
}

function check_handler(){
	var include = this.getAttribute('include');
	var exclude = this.getAttribute('exclude');

	if(include){
		var targets = document.getElementsByClassName(include);
		for( var i = 0; i < targets.length; i++ ){
			targets[i].checked = this.checked;
		}
	}

	if(exclude){
		var targets = document.getElementsByClassName(exclude);
		for( var i = 0; i < targets.length; i++ ){
			if(targets[i]!=this){
				targets[i].checked = !this.checked;
			}
		}
	}

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
	globals.summary.innerHTML = response.summary;
}

// -----------------------------------------------------------------------------
// REQUESTORS: of endpoints
// -----------------------------------------------------------------------------
function load_requestor(){
	var pk = this.getAttribute('pk');
	network.get('articles', { id:pk });

	globals.pk = pk;

	if(globals.title){
		globals.title.classList.remove('highlighted');
	}
	this.classList.add('highlighted');
	globals.title = this;
}

function refresh_requestor(){
	if(globals.pk!=null){
		var people_str = globals.people.join(';');
		network.post('refresh', { pk:globals.pk, people:people_str })
	}
}

function summary_requestor( element ){
	var name = element.getAttribute('name');

	var summary = document.createElement('div');
	summary.className = 'summary';
	summary.innerHTML = '<div class="loader"></div>';

	element.attach_front( summary );
	if(globals.summary!=null){
		globals.summary.delete();
	}
	globals.summary = summary;
	network.get('annotations',{ name:name })
}

// -----------------------------------------------------------------------------
// LISTENER DECLARATIONS
// -----------------------------------------------------------------------------
window.addEventListener('scroll',scroll_handler);

layout.all_check.addEventListener('change',check_handler);
layout.reg_check.addEventListener('change',check_handler);
layout.pla_check.addEventListener('change',check_handler);

layout.content.addEventListener('mouseup',select_handler);


for( var i = 0; i < layout.titles.length; i++ ){
	layout.titles[i].addEventListener('click',load_requestor);
}
