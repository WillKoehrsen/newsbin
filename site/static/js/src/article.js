// -----------------------------------------------------------------------------
// Localize the datetime on under the title
var block = document.getElementById('js-localize-date');
if(block!=null){
	var date = new Date( block.getAttribute('iso') );
	block.innerHTML = date.toLocaleDateString() + " " + date.toLocaleTimeString();
}

// -----------------------------------------------------------------------------
// customize document prototype
HTMLDocument.prototype.createElementWithAttr = function( tag, attrs ){
	var elem = this.createElement(tag);
	for(attr in attrs){ elem.setAttribute(attr,attrs[attr]); }
	return elem;
}

// -----------------------------------------------------------------------------
// Annotation:
//		a modal component that displays when an x-annotation is clicked
var modal = (function( target ){
	var layout = {
		modal:document.getElementById( target ),
		contents:document.createElementWithAttr('div',{class:'modal-container'}),
		part:{
			close:document.createElementWithAttr('div',{class:'modal-close',onClick:'modal.close()'}),
			title:document.createElementWithAttr('div',{class:'modal-title'}),
			image:document.createElementWithAttr('img',{class:'modal-image'}),
			content:document.createElementWithAttr('div',{class:'modal-content'}),
			link:document.createElementWithAttr('a',{class:'modal-link',target:'_blank'}),
		},
	}
	// add content to the modal window
	layout.modal.appendChild(layout.contents);
	for(item in layout.part){ layout.contents.appendChild(layout.part[item]); }

	layout.part.link.innerHTML = "wikipedia";
	layout.part.close.innerHTML = "Close";

	var operations = {
		display:function( name ){
			var handle = new XMLHttpRequest();
			var url = '/annotations?name=' + name;
			handle.onload = function(){
				if(this.status==200){
					var response = JSON.parse(this.responseText);
					layout.part.title.innerHTML = response.name;
					layout.part.image.setAttribute('src',response.image);
					layout.part.content.innerHTML = response.summary;
					layout.part.link.setAttribute('href','https://en.wikipedia.org/wiki/' + response.name);
					layout.modal.style.display = "flex";

					console.log('TRUTH RATING: ',response.truth_score)
				}
			}
			handle.open("GET", url, true);
			handle.send();
		},

		close:function(){
			layout.part.title.innerHTML = "";
			layout.part.image.setAttribute('src',"#");
			layout.part.content.innerHTML = "";
			layout.part.link.setAttribute('href','#');
			layout.modal.style.display = "none";
		},
	}

	return operations;
})( 'js-annotation-modal' );

var annotations = document.getElementsByClassName('annotation');
if(annotations){
	for( var i = 0; i < annotations.length; i++ ){
		annotations[i].addEventListener("click", function(_event){
			modal.display(this.getAttribute('name'));
		});
	}
}

var content = document.getElementById('js-capture-selection');
if(content){
	content.addEventListener('mouseup',function(){
		var selection = window.getSelection();
		if( !selection.isCollapsed && selection.rangeCount==1 ){
			var range = selection.getRangeAt(0);
			var input = document.getElementById('js-add-selection');
			if( input && range ){
				input.value = range.toString();
			}
		}
	});
}
