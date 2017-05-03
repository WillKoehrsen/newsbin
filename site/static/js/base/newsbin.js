// -----------------------------------------------------------------------------
// GLOBAL VARIABLES
// -----------------------------------------------------------------------------
var minus = '&minus;';

var article = document.getElementById('article');
var article_start = parseInt(window.getComputedStyle(article).marginTop);
var all = document.getElementById('all');
var regex = document.getElementById('regex');
var plain = document.getElementById('plain');

globals = {
	people: null,
	pk: null,
	summary: null,
}

layout = {
	// top DOM elements
	all_check: document.querySelector('#all_check'),
	reg_check: document.querySelector('#reg_check'),
	pla_check: document.querySelector('#pla_check'),

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

	// a global to track the last highlighted text
	last_capture:null,

	// a global to track the last highlighted title
	last_title:null,
}

// -----------------------------------------------------------------------------
// RESPONSE HANDLERS
function load_handler( response ){

	// build the html for the people list at the bottom
	// of the article
	var people_html = '';
	globals.people = response.people.split(';').filter(function(entry) { return entry.trim() != ''; });
	for( var i=0; i<globals.people.length; i++){
		people_html += '<span class="name">' + globals.people[i].trim() + '<x-remove onmousedown="remove_handler( this.parentNode )">&minus;</x-remove></span>';
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
		people_html += '<span class="name">' + globals.people[i].trim() + '<x-remove onmousedown="remove_handler( this.parentNode )">&minus;</x-remove></span>';
	}

	layout.content.innerHTML = response.content;
}

function scroll_handler(){
	var top = layout.article.getBoundingClientRect().top;
	var old_margin = parseInt(window.getComputedStyle(layout.article).marginTop);
	var new_margin = (-top)+old_margin;

	if(new_margin<article_start){
		layout.article.style.marginTop = article_start + 'px';
	} else {
		layout.article.style.marginTop = new_margin + 'px';
	}
}

function select_handler() {
	var last = layout.last_capture;
	if (last!=null && last.parentNode!=null){
		var children = last.childNodes;
		var nodes = [];
		for(var i = 0; i < children.length; i++){
			var node = children[i];
			if(node.nodeName!='X-ADD'){
				nodes.push(node);
			}
		}
		for(var i = 0; i < nodes.length; i++){
			last.parentNode.insertBefore( nodes[i], last );
		}
		last.parentNode.removeChild( last );
	}

	if( typeof(window.getSelection) != "undefined" ){
		var selection = window.getSelection();
		var range = selection.getRangeAt(0);

		if( selection.rangeCount > 0 && !range.collapsed ) {
			var new_capture = document.createElement("x-capture");

			try {
				range.surroundContents(new_capture);
				var new_range = document.createRange();
				new_range.selectNodeContents(new_capture);
				selection.removeAllRanges();
				selection.addRange(new_range);

				var add_button = create_node('<x-add onmousedown="add_handler( this.parentNode )">&plus;</x-add>');
				new_capture.appendChild(add_button);
				layout.last_capture = new_capture;
			} catch ( error ){

			}
		}
	}
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

function add_handler( element ){
	if(globals.people!=null){
		var name = get_text( element );
		if (globals.people.indexOf(name)<0){
			globals.people.push(name);
			layout.people.innerHTML += '<span class="name">' + name + '<x-remove onmousedown="remove_handler( this.parentNode )">&minus;</x-remove></span>';
			refresh_requestor();
		}
	}
}

function remove_handler( element ){
	if(globals.people!=null){
		var name = get_text( element );
		var index = globals.people.indexOf(name);
		if( index >= 0 ){
			globals.people.splice( index, 1 );
			element.parentNode.removeChild( element );
			refresh_requestor();
		}
	}
}

function summary_handler( element ){
	//console.log(element);
}

// -----------------------------------------------------------------------------
// REQUESTORS
function load_requestor(){
	var pk = this.getAttribute('pk');
	network.get('articles', { id:pk });

	globals.pk = pk;

	if(layout.last_title){
		layout.last_title.classList.remove('highlighted');
	}
	this.classList.add('highlighted');
	layout.last_title = this;
}

function refresh_requestor(){
	if(globals.pk!=null){
		var people_str = globals.people.join(';');
		network.post('refresh', { pk:globals.pk, people:people_str })
	}
}

function summary_requestor( element ){
	//console.log(element);
	//var name = element.getAttribute('name');

	//var summary = create_node('<div class="summary"><div class="loader"></div></div>');
	//element.parentNode.insertBefore( new_summary, element );

	//if(globals.summary!=null){
	//	globals.summary.parentNode.removeChild( globals.summary );
	//}

	//globals.summary = summary;
	//network.get('annotations',{ name:name }
}

// -----------------------------------------------------------------------------
// LISTENERS (EVENTS)
window.addEventListener('scroll',scroll_handler);

layout.all_check.addEventListener('change',check_handler);
layout.reg_check.addEventListener('change',check_handler);
layout.pla_check.addEventListener('change',check_handler);

layout.content.addEventListener('mouseup',select_handler);

for( var i = 0; i < layout.titles.length; i++ ){
	layout.titles[i].addEventListener('click',load_requestor);
}

// -----------------------------------------------------------------------------
// FUNCTIONS (MAIN)
// -----------------------------------------------------------------------------

// create the string for x-add elements
function create_add( value ){

}

// create the string for x-remove elements
function create_remove( value ){

}

// create an object (or collection of objects) from an html string
function create_node( html ){
	var div = document.createElement('div');
	div.innerHTML = html;
	children = div.childNodes;
	return children[0];
}

function create_nodes( html ){
	var div = document.createElement('div');
	div.innerHTML = html;
	children = div.childNodes;
	return children;
}

// returns just text from an element
function get_text( element ){
	var node = element.cloneNode();
	node = remove_add( node );
	return node.textContent;
}

function remove_add( element ){
	var children = element.childNodes;
	for(var i = 0; i < children.length; i++){
		if(children[i]=='X-ADD'){
			element.removeChild( children[i] );
		}
	}
	return element;
}
