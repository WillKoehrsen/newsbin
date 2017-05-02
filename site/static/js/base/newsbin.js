// -----------------------------------------------------------------------------
// GLOBAL VARIABLES
// -----------------------------------------------------------------------------
var minus = '&minus;';

var article = document.getElementById('article');
var article_start = parseInt(window.getComputedStyle(article).marginTop);
var all = document.getElementById('all');
var regex = document.getElementById('regex');
var plain = document.getElementById('plain');

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
	var people_html = '';
	people = response.people.split(';');
	for( var i=0; i<people.length; i++){
		people_html += '<span class="name">' + people[i].trim() + '<x-remove onmousedown="remove_handler( this.parentNode )">&minus;</x-remove></span>';
	}
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
	layout.content.innerHTML = response.content;
	layout.people.innerHTML = get_people( response.people );
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
		var text = get_text( last );
		last.parentNode.replaceChild( text, last );
	}

	if( typeof(window.getSelection) != "undefined" ){
		var selection = window.getSelection();
		var range = selection.getRangeAt(0);

		if( selection.rangeCount > 0 && !range.collapsed ) {
			var new_capture = document.createElement("x-capture");

			console.log(typeof(selection),typeof(range));
			range.surroundContents(new_capture);

			var new_range = document.createRange();
			new_range.selectNodeContents(new_capture);
			selection.removeAllRanges();
			selection.addRange(new_range);

			var add_button = create_node('<x-add onmousedown="add_handler( this.parentNode )">&plus;</x-add>');
			new_capture.appendChild(add_button);
			layout.last_capture = new_capture;
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
	console.log( element );
	//var name = get_text( element );
	//if (people.indexOf(name)<0){
	//	people.push(name);
	//	var div = document.querySelector("#article>#people");
	//	div.innerHTML += '<span class="name">' + name + '<x-remove onmousedown="remove_annotation( this.parentNode )">' + minus + '</x-remove></span>';
	//	refresh();
	//}
}

function remove_handler(){
	console.log('REMOVE');
}

// -----------------------------------------------------------------------------
// REQUESTORS
function load_requestor(){
	var pk = this.getAttribute('pk');
	network.get('articles', { id:pk })


	if(layout.last_title){
		layout.last_title.classList.remove('highlighted');
	}
	this.classList.add('highlighted');
	layout.last_title = this;
}

function refresh_requestor(){
	var pk = this.getAttribute('pk');
	network.get('refresh', { id:pk })
}

// -----------------------------------------------------------------------------
// LISTENERS (EVENTS)
window.addEventListener('scroll',scroll_handler);
layout.content.addEventListener('mouseup',select_handler);

layout.all_check.addEventListener('change',check_handler);
layout.reg_check.addEventListener('change',check_handler);
layout.pla_check.addEventListener('change',check_handler);


for( var i = 0; i < layout.titles.length; i++ ){
	layout.titles[i].addEventListener('click',load_requestor);
}








// -----------------------------------------------------------------------------
// FUNCTIONS (MAIN)
// -----------------------------------------------------------------------------

//function show_summary( element ){
//	var caller = element;
//	var name = caller.getAttribute('name');
//	var url = '/annotations?name=' + name;
//	var request = new XMLHttpRequest();
//
//	var new_summary = create_node('<div class="summary"><div class="loader"></div></div>');
//	caller.parentNode.insertBefore( new_summary, caller );
//
//	if(current_summary){
//		remove( current_summary );
//	}
//	current_summary = new_summary;
//
//	request.onreadystatechange = function() {
//		if (request.readyState == 4 && request.status == 200){
//			new_summary.innerHTML = request.responseText;
//		}
//	}
//	request.open("GET", url, true); // true for asynchronous
//	request.send(null);
//}
//
//
//function add_annotation( element ){
//	var name = get_text( element );
//	if (people.indexOf(name)<0){
//		people.push(name);
//		var div = document.querySelector("#article>#people");
//		div.innerHTML += '<span class="name">' + name + '<x-remove onmousedown="remove_annotation( this.parentNode )">' + minus + '</x-remove></span>';
//		refresh();
//	}
//}

function remove_annotation(){
	console.log('remove annotation');
}

function refresh(){
	console.log('refresh');
}


// -----------------------------------------------------------------------------
// FUNCTIONS (UTILITIES)
// -----------------------------------------------------------------------------

// create an object (or collection of objects) from an html string
function create_node( html ){
	var div = document.createElement('div');
	div.innerHTML = html;
	children = div.childNodes;
	if(children.length!=1){
		return children;
	}
	return children[0];
}

// returns just text from an element
function get_text( element ){
	var result = '';
	var children = element.childNodes;
	for( var i = 0; i < children.length; i++ ){
		if(children[i].nodeType==3){
			result += children[i].textContent;
		}
	}
	var node = document.createTextNode(result.trim());
	return node;
}
