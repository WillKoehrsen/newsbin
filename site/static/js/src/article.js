// -----------------------------------------------------------------------------
// implement forEach if we're in IE
if (!NodeList.prototype.forEach) {
    NodeList.prototype.forEach = function(fn, scope) {
        for(var i = 0, len = this.length; i < len; ++i) {
            fn.call(scope, this[i], i, this);
        }
    }
}

/* -----------------------------------------------------------------------------
	MODAL

		This immediately invoked function returns a set of handlers that can
		fill and open/ empty and close the modal window to display annotations:

		1.	Shortcuts the children of the modal window to the modal element
			itself for conveniance.

		2.	Creates a handler object that contains two functions:

				close: empties and closes the modal window
				open: fetches data, fills and opens the modal window
*/
var modal = (function( target ){
	target.refs = {};
	var children = target.getElementsByTagName('div');
	for( var i=0; i<children.length; i++ ){
		var ref = children[i].getAttribute('ref');
		if(ref){ target.refs[ref] = children[i]; }
	}

	handlers = {
		close:function(){
			for(ref in target.refs){ target.refs[ref].innerHTML = ''; }
			target.style.display = 'none';
		},
		open:function( annotation ){
			var refs = target.refs;

            handlers.close();

			refs.close.innerHTML = 'Close';
			refs.title.innerHTML = annotation.name;
			refs.image.innerHTML = '<img src="'+annotation.image+'"/>';

			var content = annotation.summary.split('\n\n')
			content.forEach(function( p ){
				refs.content.innerHTML += '<p>'+p+'</p>';
			});

			refs.links.innerHTML += '<a href="https://en.wikipedia.org/wiki/'+annotation.name+'" target="_blank">on wikipedia</a>';
			if(annotation.slug && annotation.slug!='None'){ refs.links.innerHTML += '<a href="http://www.politifact.com/personalities/'+annotation.slug+'" target="_blank">on politifact</a>'; }

            data = annotation.data_table;
            for( var i=0; i<data.length; i++ ){
                var item = data[i];
                refs.data.innerHTML += '<div class="modal-data-item">\
											<div>'+item.key+'</div>\
											<div>'+item.value+'</div>\
										</div>';
                //tooltips.add(refs.data.lastChild);
            }

			target.style.display = 'flex';
		},
	}

	return handlers;
})( document.getElementById('js-modal-annotation') );

/* -----------------------------------------------------------------------------
	ANNOTATIONS

		This immediately invoked function adds an 'onclick'
		event handler that launches the modal window.
*/
var annotations = (function(){
    var storage = [];
    var active = true;
    function open_modal( _event ){
        if(active){
            var anno = handlers.get( this.getAttribute('id') );
            modal.open( anno );
        }
    }

    var handlers = {

        disable:function(){
            active = false;
            var annotations = document.getElementsByClassName('annotation')
            for( var i = 0; i < annotations.length; i++ ){
                annotations[i].classList.remove('highlight');
    		}
        },

        enable:function(){
            active = true;
            var annotations = document.getElementsByClassName('annotation')
            for( var i = 0; i < annotations.length; i++ ){
                annotations[i].classList.add('highlight');
    		}
        },

        refresh:function(){
            var annotations = document.getElementsByClassName('annotation')
            var toggle = document.getElementById('js-eye-toggle');
            for( var i = 0; i < annotations.length; i++ ){
                var anno = annotations[i];
                anno.removeEventListener('click', open_modal, false);
                anno.addEventListener("click", open_modal);
                if(toggle.classList.contains('active-toggle')){
                    anno.classList.add('highlight');
                }
            }
        },

        add:function( annotation ){
            for(var i=0; i<storage.length; i++){
                if(annotation.id==storage[i].id){ return false; }
            }
            storage.push( annotation );
            return true;
        },

        get:function( id ){
            for(var i=0; i<storage.length; i++){
                var item = storage[i];
                if(id==item.id){ return item; }
            }
        },

        test:function(){
            console.log(storage);
        },

    }
    handlers.refresh();
    handlers.enable();
    return handlers;
})();

/* -----------------------------------------------------------------------------
	CONTENT

		Watch the content area of an article for selections and
		copy the text to the annotation submission.
*/
(function( content, input ){
	if(content){
		content.addEventListener('mouseup',function(){
			var selection = window.getSelection();
			if( !selection.isCollapsed && selection.rangeCount==1 ){
				var range = selection.getRangeAt(0);;
				if( input && range ){
					input.value = range.toString();
				}
			}
		});
	}
})(
	document.getElementById('js-article-content'),
	document.getElementById('js-add-selection')
);

/* -----------------------------------------------------------------------------
	DATE

		Sets the date in the copyright notice
*/
(function( block ){
    if(block){
        block.innerHTML = (new Date()).getFullYear();
    }
})(document.getElementById('js-year'));

/* -----------------------------------------------------------------------------
	EYE TOGGLE

		This adds a 'click' eventlistener to the 'eye' in the menu
        that toggles the display of annotations in the article
*/
(function( eye, eye_btn ){
    if( eye && eye_btn ){
        if(eye.id in sessionStorage){
            var initial = sessionStorage.getItem(eye.id)!='false';
            if(initial){
                eye.classList.add('active-toggle');
                annotations.enable();
            } else {
                eye.classList.remove('active-toggle');
                annotations.disable();
            }
        }
        eye_btn.addEventListener('click',function(){
            if(eye.classList.toggle('active-toggle')){
                annotations.enable();
                window.sessionStorage.setItem(eye.id,true);
            } else {
                annotations.disable();
                window.sessionStorage.setItem(eye.id,false);
            }
        });
    }
})(
    document.getElementById('js-eye-toggle'),
    document.getElementById('js-eye-btn')
);

/* -----------------------------------------------------------------------------
	ANNOTATE ARTICLE

		This fetches and wraps annotations in the article.
*/
(function( target ){

	function annotate( element, regex, annos ){
		if(element.tagName!='A'){
			var content = '';
			for( var i = 0; i < element.childNodes.length; i++ ){
				var node = element.childNodes[i];
				switch( node.nodeType ){
					case 1: // a nested element that we need to recurse into
						node.innerHTML = annotate( node, regex, annos );
						content += node.outerHTML;
						break;
					case 3: // a textnode that we need to parse
						content += node.nodeValue.replace(regex,function( value, index, text ){             // replace matches with new span
                            var current = null;
                            for( var i = 0; i < annos.length; i++){
                                var anno = annos[i];
                                if(anno.name==value){
                                    current = anno;
                                    break;
                                }
                            }
                            annotations.add(current);
                            return '<span class="annotation" id="' + current.id + '">' + value + '</span>';
						});
						break;
					default:
						break;
				}
			}
			return content;
		}
		else {
			return element.outerHTML;
		}
	}

    var handle = new XMLHttpRequest();

    handle.onload = function(){
        if(this.status==200){
            try {
                var response = JSON.parse(this.responseText);

                // sort by length and alphabetically if the same length
                var values = response.sort(function(a,b){
                    return b.name.length - a.name.length || a.name.localeCompare(b.name);
                });

                // build names
                names = []
                for(var i = 0; i < values.length; i++){
                    names.push(values[i].name);
                }
                var regex = new RegExp(names.join('|'),'g');
                target.innerHTML = annotate( target, regex, values );
                annotations.refresh();
            } catch(err){
                console.log(err);
            }
        }
    }

    handle.open("GET", '/articles/' + DATA.id + '/annotations', true);
    handle.send();
})(document.getElementById('js-article-content'));
