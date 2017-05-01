// -----------------------------------------------------------------------------
// Functions

// build a url from a given base and arguments
function url( base, obj ){
	result = [];
	for( var key in obj ){ result.push( key+'='+obj[key].replace(' ','%20') ); }
	if( result.length > 0 ){ result.unshift('?'); }
	return base + result.join('&');
}

// -----------------------------------------------------------------------------
// Network
var network = {
	// An interface for registering local endpoints
	// and then sending and receiving JSON data

	points:{},

	get: function( endpoint, args ){
		if(endpoint in network.points){
			var handle = new XMLHttpRequest();
			var path = url( endpoint, args );

			handle.callback = network.points[endpoint];
			handle.onload = this.receive;
			handle.onerror = this.error;

			handle.open("GET", path, true);
			handle.send();
		}
	},

	post: function( endpoint, args ){
		if(endpoint in this.points){
			var handle = new XMLHttpRequest();
			var path = url( endpoint );
			var form = new FormData();

			for( var key in args ){
				form.append(key,args[key]);
			}

			handle.callback = network.points[endpoint];
			handle.onload = this.receive;
			handle.onerror = this.error;

			handle.open("POST", path, true);
			handle.send(form);
		}
	},

	register: function( endpoint, callback ){
		network.points[endpoint] = callback;
	},

	receive: function(){
		var response = JSON.parse(this.responseText);
		this.callback(response);
	},

	error: function(){
		console.log(this);
	}

}
