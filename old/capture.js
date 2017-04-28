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
