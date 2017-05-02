// -----------------------------------------------------------------------------
// String extensions
String.prototype.prependif = function( ch ){
	if(this.substring(0,ch.length) != ch ){
		return ch + this;
	} else {
		return this.toString();
	}
}
