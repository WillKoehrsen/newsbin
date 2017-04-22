/*
	NEWSBIN.JS:
		This is the javascript that handles the front end of the newsbin website,
		The other parts of the newsbin system are the website itself (a minimalist
		Flask app in python) and the NEWSBIN.PY module.
*/

function remove( element ) {
	element.parentNode.removeChild( element );
}

// REMEMBER: make sure there is some visual representation of the currently selected title.

function Article( id ) {

	// Initialization sets provided options to given values or defaults
	this.init = function( pk ){
		this.id = pk;
		this.parent = 'article_contents';
		this.refresh();
	}

	this.refresh = function(){
		this.loading();
		var xhttp = new XMLHttpRequest();
		var url = '/articles?data=' + encodeURIComponent(this.serialize());
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

	this.deserialize = function( values ){
		object = JSON.parse( values );
		for( var attribute in object ){ if(typeof(this[attribute])!='function'){ this[attribute] = object[attribute]; } }
	}

	this.serialize = function(){
		obj = {};
		for( var attribute in this ){ if(typeof(this[attribute])!='function'){ obj[attribute] = this[attribute]; } }
		return JSON.stringify(obj);
	}

	this.fill = function(){
		block = document.getElementById( this.parent );
		block.innerHTML = this.html();
	}

	this.loading = function(){
		block = document.getElementById( this.parent );
		block.innerHTML = '<div class="loader"></div>';
	}

	this.get_people = function(){
		arr_list = this.people.split(';');
		var str_list = '';
		for( var i=0; i<arr_list.length; i++){
			str_list += '<span class="name">' + arr_list[i] + '<x-remove onmousedown="remove( this.parentNode )">&minus;</x-remove></span>';
		}
		return str_list;
	}

	this.set_people = function(){

	}

	this.html = function(){
		var people = this.get_people();
		html = 	'<div id="header">' +
				'  <span id="title">' + this.title + '</span><br/>' +
				'  <span id="author">AUTHOR: ' + this.author + '</span>' +
				'  <span id="publish_date">PUBLISHED: ' + this.publish_date + '</span>' +
				'</div>' +
				'<div id="content">' +
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
