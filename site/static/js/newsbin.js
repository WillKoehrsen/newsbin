// -----------------------------------------------------------------------------
// GLOBAL VARIABLES
// -----------------------------------------------------------------------------
var people = [];

var plus = '&plus;';
var minus = '&minus;';

var article = document.getElementById('article');
var article_start = parseInt(window.getComputedStyle(article).marginTop);
var all = document.getElementById('all');
var regex = document.getElementById('regex');
var plain = document.getElementById('plain');

// -----------------------------------------------------------------------------
// LISTENERS (EVENTS)
// -----------------------------------------------------------------------------

// event listener to move article into view on scroll
window.addEventListener('scroll',recenter_article);

// event listener to capture highlights in text
document.getElementById('article').addEventListener('onmouseup',watch);

// when the 'all' checkbox changes, update all source checkboxes
all.addEventListener('change',function(){
	var dependents = document.getElementsByClassName('all_dependent');
	for( var i=0; i<dependents.length; i++ ){
		dependents[i].checked = this.checked;
	}
});

// on 'regex' checkbox change, set 'plain' to the opposite
regex.addEventListener('change',function(){ plain.checked = !this.checked; });

// on 'plain' checkbox change, set 'regex' to the opposite
plain.addEventListener('change',function(){ regex.checked = !this.checked; });

// -----------------------------------------------------------------------------
// FUNCTIONS (MAIN)
// -----------------------------------------------------------------------------

// move the article display to stay in the viewport
function recenter_article(){
	var top = article.getBoundingClientRect().top;
	var old_margin = parseInt(window.getComputedStyle(article).marginTop);
	var new_margin = (-top)+old_margin;

	if(new_margin<article_start){
		article.style.marginTop = article_start + 'px';
	} else {
		article.style.marginTop = new_margin + 'px';
	}
}

// fetches an article by id and fills '#article'
function fetch_article( id, element ){
	highlight_title( element );
	load( id );
}

// watches for highlight events and captures the selection
function watch() {
	dump_capture( this.last_capture );
	var new_capture = capture();
	this.last_capture = new_capture;
}

// captures highlighted text
function capture() {
	if (typeof window.getSelection != "undefined") {
		selection = window.getSelection()
		if (selection.rangeCount > 0) {
			var range = selection.getRangeAt(0);
			if (!range.collapsed) {
				var newNode = document.createElement("x-capture");
				try {
					range.surroundContents(newNode);
					var newRange = document.createRange();
					newRange.selectNodeContents(newNode);
					selection.removeAllRanges();
					selection.addRange(newRange);

					var add_button = create_node('<x-add onmousedown="add_annotation( this.parentNode )">' + plus + '</x-add>');
					newNode.appendChild(add_button);
					return newNode
				}
				catch (err) {
					return null
				}
			}
		}
	}
	return null
}

function show_summary( element ){
	var caller = element;
	var name = caller.getAttribute('name');
	var url = '/annotations?name=' + name;
	var request = new XMLHttpRequest();

	var new_summary = create_node('<div class="summary"><div class="loader"></div></div>');
	caller.parentNode.insertBefore( new_summary, caller );

	if(current_summary){
		remove( current_summary );
	}
	current_summary = new_summary;

	request.onreadystatechange = function() {
		if (request.readyState == 4 && request.status == 200){
			new_summary.innerHTML = request.responseText;
		}
	}
	request.open("GET", url, true); // true for asynchronous
	request.send(null);
}

function load( id ){
	article.innerHTML = '<div class="loader"></div>';
	var xhttp = new XMLHttpRequest();
	var url = '/articles?id=' + id;
	xhttp.onreadystatechange = function(){
		if (this.readyState == 4 && this.status == 200) {
			object = JSON.parse( this.responseText );
			object.people = get_people( object.people );
			article.innerHTML = build_html( object );
	   }
	};
	xhttp.open("GET", url, true);
	xhttp.send();
}

function build_html( object ){
	html = 	'<div id="header">' +
			'  <span id="title">' + object.title + '</span><br/>' +
			'  <span id="author">AUTHOR: ' + object.author + '</span>' +
			'  <span id="publish_date">PUBLISHED: ' + object.publish_date + '</span>' +
			'</div>' +
			'<div id="content" onmouseup="watch()">' +
			   object.content +
			'</div>' +
			'<div id="people">' +
			   object.people +
			'</div>' +
			'<div id="footer">' +
			'  <span id="id">ID: ' + object.id + '</span>' +
			'  <span id="source">SOURCE: ' + object.source + '</span>' +
			'  <span id="link">ORIGINAL: <a href="' + object.link + '">link</a></span>' +
			'</div>';
	return html;
}

// convert a semi-colon delimited string of names into html
function get_people( names ){
	var str_list = '';
	people = names.split(';');
	for( var i=0; i<people.length; i++){
		str_list += '<span class="name">' + people[i].trim() + '<x-remove onmousedown="remove_annotation( this.parentNode )">' + minus + '</x-remove></span>';
	}
	return str_list;
}

function add_annotation( element ){
	var name = get_text( element );
	if (people.indexOf(name)<0){
		people.push(name);
		var div = document.querySelector("#article>#people");
		div.innerHTML += '<span class="name">' + name + '<x-remove onmousedown="remove_annotation( this.parentNode )">' + minus + '</x-remove></span>';
		refresh();
	}
}

function remove_annotation(){
	console.log('remove annotation');
}

function refresh(){
	console.log('refresh');
}


// -----------------------------------------------------------------------------
// FUNCTIONS (UTILITIES)
// -----------------------------------------------------------------------------

// extract top-level text from node and replace node with text
function dump_capture( element ) {
	if (element!=null && element.parentNode!=null){
		var text = document.createTextNode( get_text( element ) );
		element.parentNode.replaceChild( text, element );
	}
}

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
	var newNode = element.cloneNode(true);
	var children = newNode.children;
	for(var i = 0; i<children.length; i++){
		newNode.removeChild(children[i]);
	}
	return newNode.textContent.trim();
}

// moves 'highlighted' class from previous to current selection
function highlight_title( element ){
	element.classList.add('highlighted');
	if( this.previous ){
		this.previous.classList.remove('highlighted');
	}
	this.previous = element;
}