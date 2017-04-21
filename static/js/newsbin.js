/*
	NEWSBIN.JS:
		This is the javascript that handles the front end of the newsbin website,
		The other parts of the newsbin system are the website itself (a minimalist
		Flask app in python) and the NEWSBIN.PY module.
*/

// REMEMBER: make sure there is some visual representation of the currently selected title.

function Article( settings ) {

	// Initialization sets provided options to given values or defaults
	this.init = function( args ){
		var defaults = { id:-1, title:'Untitled', content:'t', people:'', author:'Unknown', source:'Unknown', publish_date:'Unknown' }
		defaults = overwrite( defaults, args );

		// header information
		this.title = defaults.title;
		this.author = defaults.author;
		this.publish_date = defaults.publish_date;

		// content
		this.content = defaults.content;

		// footer information
		this.people = defaults.people;
		this.source = defaults.source;
		this.id = defaults.id;

		// utility
		this.request_url = '/article/';
	}

	this.request = function (){
		var request = new XMLHttpRequest();

		request.onreadystatechange = function() {
			if (request.readyState == 4 && request.status == 200){
				console.log( request.responseText );
			}
		}

		request.open("GET", this.request_url, true); // true for asynchronous
		request.send(null);
	}

	this.submit = function (){
		console.log('submit new list of people and this.content and update this.content with reply');
	}

	this.html = function (){

		// ---------------------------------------------------------------------
		// HEADER
		// format the title and place inside a div
		var title = createItem( 'span', 'title', this.title.trim() );
		var author = createItem( 'span', 'author', this.author.trim() );
		var publish_date = createItem( 'span', 'publish_date', this.publish_date.trim() );

		var header = createSection( 'div', 'header', [ title, author, publish_date] );
		// ---------------------------------------------------------------------

		// ---------------------------------------------------------------------
		// CONTENT
		// format the content text into paragraphs

		var blocks = this.content.split('\n\n');
		for(var i = 0; i < blocks.length; i++){
			blocks[i] = createItem( 'p', '', blocks[i].trim() );
		}
		// combine the paragraphs into a single div
		var content = createSection( 'div', 'content', blocks );

		// ---------------------------------------------------------------------

		// ---------------------------------------------------------------------
		// FOOTER
		// split the people string and place each name in a span with a remove button
		var blocks = []
		if(this.people){
			blocks = this.people.split(';');
			for(var i = 0; i < blocks.length; i++){
				blocks[i] = '<span class="annotation">' + blocks[i].trim() + '<x-remove onmousedown="removeCapture( this )">&minus;</x-remove></span>';
			}
		}

			// combine the list of people into a single span
		people = '<span class="people">' + people.join('') + '</span>';

		var source = '<span class="source">' + this.source.trim() + '</span>';
		var id = '<span class="id">' + this.id + '</span>';

		var footer = '<div class="footer">' + people + source + id + '</div>'
		// ---------------------------------------------------------------------


	}

	this.init( settings )
}

/*
	FUNCTIONS
*/
function overwrite( a, b ){
	if( a ){
		if( b ){
			for( var item in b ){
				if(item){
					a[item] = b[item];
				}
			}
		}
		return a;
	}
}

function createItem( type, classname, textcontent ){
	var item = document.createElement(type);
	if(classname){ item.setAttribute('class',classname); }
	item.appendChild(document.createTextNode(textcontent));
	return item
}

function createSection( type, classname, children ){
	var item = document.createElement(type);
	if(classname){ item.setAttribute('class',classname); }
	for( var i=0; i < children.length; i++ ){
		item.appendChild(children[i]);
	}
	return item
}














var lastCapture = null;
var plus = '&plus;';
var minus = '&minus;';

function getText( element ){
	var newNode = element.cloneNode(true);
	newNode.removeChild(newNode.lastChild)
	return newNode.textContent;
}

function dumpLastCapture() {
	if (lastCapture!=null && lastCapture.parentNode!=null){
		var text = document.createTextNode( getText( lastCapture ) );
		lastCapture.parentNode.replaceChild( text, lastCapture );
	}
}

function addCapture() {
	var text = getText(this.parentNode);
	console.log( 'ADD: ' + text );
}

function removeCapture() {
	//var text = getText(this.parentNode);
	//console.log( 'REMOVE: ' + text );
	if(this.parentNode != null && this.parentNode.parentNode!=null){
		var parent = this.parentNode;
		var gparent = parent.parentNode;
		gparent.removeChild(parent);
	}
}

function markNewCapture() {
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

					var addButton = document.createElement("x-add");
					addButton.innerHTML = plus;
					addButton.onmousedown = addCapture;
					newNode.appendChild(addButton)
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

function watch() {
	dumpLastCapture();
	var newCapture = markNewCapture();
	lastCapture = newCapture;
}
