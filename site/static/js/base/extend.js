// -----------------------------------------------------------------------------
// Object extensions
Object.prototype.keys = function (){
	results = [];
	for( key in this ){if( typeof(key)!='function' ){ results.push(key); }}
	return results;
}

// -----------------------------------------------------------------------------
// String extensions
String.prototype.prependif = function( ch ){
	if(this.substring(0,ch.length) != ch ){
		return ch + this;
	} else {
		return this.toString();
	}
}
