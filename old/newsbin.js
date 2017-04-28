/*
	NEWSBIN.JS:
		This is the javascript that handles the front end of the newsbin website,
		The other parts of the newsbin system are the website itself (a minimalist
		Flask app in python) and the NEWSBIN.PY module.
*/

// REMEMBER: make sure there is some visual representation of the currently selected title.
// -----------------------------------------------------------------------------
// GLOBALS
var last_capture = null;
var plus = '&plus;';
var minus = '&minus;';

// -----------------------------------------------------------------------------
// ARTICLE
function Article( id ) {

	// Initialization sets provided options to given values or defaults
	this.init = function( pk ){
		this.parent = 'article_contents';
		this.id = pk
		this.load( pk );
	}

	this.load = function( id ){
		this.loading();
		var xhttp = new XMLHttpRequest();
		var url = '/articles?id=' + id;
		article = this;
	    xhttp.onreadystatechange = function(){
	        if (this.readyState == 4 && this.status == 200) {
	            article.deserialize( this.responseText );
				article.fill();
	       }
	    };

	    xhttp.open("GET", url, true);
	    xhttp.send();
	}

	this.refresh = function(){
		var content = document.getElementById(this.parent).querySelector('#content');
		var xhttp = new XMLHttpRequest();
		var url = '/articles?id=' + this.id + '&people=' + this.people.join(';');

	    xhttp.onreadystatechange = function(){
	        if (this.readyState == 4 && this.status == 200) {
	            response = JSON.parse( this.responseText );
				if( 'content' in response ){
					content.innerHTML = response['content'];
				}
	       }
	    };

	    xhttp.open("GET", url, true);
	    xhttp.send();
	}

	this.deserialize = function( values ){
		object = JSON.parse( values );
		for( var attribute in object ){ if(typeof(this[attribute])!='function'){ this[attribute] = object[attribute]; } }
		if(this.people){
			this.people = this.people.split(';');
		}
		else {
			this.people = [];
		}
	}

	this.fill = function(){
		var block = document.getElementById( this.parent );
		block.innerHTML = this.html();
	}

	this.loading = function(){
		block = document.getElementById( this.parent );
		block.innerHTML = '<div class="loader"></div>';
	}

	this.get_people = function(){
		var str_list = '';
		for( var i=0; i<this.people.length; i++){
			str_list += '<span class="name">' + this.people[i] + '<x-remove onmousedown="current.remove( this.parentNode )">' + minus + '</x-remove></span>';
		}
		return str_list;
	}

	this.remove = function( element ) {
		var name = get_text( element );
		var index = this.people.indexOf(name);
	    if (index > -1) {
	       this.people.splice(index, 1);
		   remove(element);
	    }
		this.refresh();
	}

	this.add = function( element ) {
		var name = get_text( element ).trim();
		if (this.people.indexOf(name)<0){
			this.people.push(name);
			var people = document.querySelector("#article_contents>#people");
			people.innerHTML += '<span class="name">' + name + '<x-remove onmousedown="current.remove( this.parentNode )">' + minus + '</x-remove></span>';
		}
		this.refresh();
	}

	this.html = function(){
		var people = this.get_people();
		html = 	'<div id="header">' +
				'  <span id="title">' + this.title + '</span><br/>' +
				'  <span id="author">AUTHOR: ' + this.author + '</span>' +
				'  <span id="publish_date">PUBLISHED: ' + this.publish_date + '</span>' +
				'</div>' +
				'<div id="content" onmouseup="watch()">' +
				   this.content +
				'</div>' +
				'<div id="people">' +
				   people +
				'</div>' +
				'<div id="footer">' +
				'  <span id="id">ID: ' + this.id + '</span>' +
				'  <span id="source">SOURCE: ' + this.source + '</span>' +
				'  <span id="link">ORIGINAL: <a href="' + this.link + '">link</a></span>' +
				'</div>';
		return html;
	}

	this.init( id )
}

// -----------------------------------------------------------------------------
// Functions
function get_text( element ){
	var newNode = element.cloneNode(true);
	remove(newNode.lastChild);
	return newNode.textContent;
}

function watch() {
	dump_capture( last_capture );
	var new_capture = capture();
	last_capture = new_capture;
}

function dump_capture( element ) {
	if (element!=null && element.parentNode!=null){
		var text = document.createTextNode( get_text( element ) );
		element.parentNode.replaceChild( text, element );
	}
}

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

					var add_button = create('<x-add onmousedown="current.add( this.parentNode )">'+ plus +'</x-add>');
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

function create( html ){
	var div = document.createElement('div');
	div.innerHTML = html;
	children = div.childNodes;
	if(children.length!=1){
		return children;
	}
	return children[0];
}

function remove( element ){
	element.parentNode.removeChild(element);
}
