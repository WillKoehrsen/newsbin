// -----------------------------------------------------------------------------
// String extensions
String.prototype.prependif = function( ch ){
	if( this.substring(0,ch.length) != ch ){
		return ch + this;
	} else {
		return this.toString();
	}
}

// -----------------------------------------------------------------------------
// DOM extensions
Node.prototype.delete = function(){
	if( this.parentNode ){
		this.parentNode.removeChild( this );
	}
}

Node.prototype.attach_front = function( element ){
	if( this.parentNode && element ){
		this.parentNode.insertBefore( element, this );
	}
}

Node.prototype.attach_back = function( element ){
	if( this.parentNode && element && this.nextSibling ){
		this.parentNode.insertBefore( element, this.nextSibling );
	}
}
