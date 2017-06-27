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
		open:function( name ){
			var handle = new XMLHttpRequest();
			var refs = target.refs;

			handle.onload = function(){
				if(this.status==200){
                    handlers.close();
					var response = JSON.parse(this.responseText);
					refs.close.innerHTML = 'Close';
					refs.title.innerHTML = response.name;
					refs.image.innerHTML = '<img src="'+response.image+'"/>';

					var content = response.summary.split('\n\n')
					content.forEach(function( p ){
						refs.content.innerHTML += '<p>'+p+'</p>';
					});

					refs.links.innerHTML += '<a href="https://en.wikipedia.org/wiki/'+response.name+'" target="_blank">on wikipedia</a>';
					if(response.slug){ refs.links.innerHTML += '<a href="http://www.politifact.com/personalities/'+response.slug+'" target="_blank">on politifact</a>'; }

					response.data_table.forEach(function( item ){
						refs.data.innerHTML += '<div class="modal-data-item" tooltip="'+item.tooltip+'">\
													<div>'+item.key+'</div>\
													<div>'+item.value+'</div>\
												</div>';
                        tooltips.add(refs.data.lastChild);
                    });
					target.style.display = 'flex';
				} else {
					console.log(this.status);
				}
			}

			handle.open("GET", '/annotations?name=' + name, true);
			handle.send();
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
    var active = true;
    function open_modal( _event ){
        if(active){
            modal.open(this.getAttribute('name'));
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
            var toggle = document.getElementById('eye-toggle');
            for( var i = 0; i < annotations.length; i++ ){
                var anno = annotations[i];
                anno.removeEventListener('click', open_modal, false);
                anno.addEventListener("click", open_modal);
                if(toggle.classList.contains('active-toggle')){
                    anno.classList.add('highlight');
                }
            }
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
	MOBILE MENU

		This bit adds a 'click' eventlistener that toggles the tabs and
		hides/displays the mobile menu. Tabs define functions to run from
		handlers with the 'run' attribute.
*/
(function( menu, options ){
	var tabs = [];
	[].push.apply(tabs, menu.getElementsByTagName('div'));

	var handlers = {
		open_menu:function(){options.classList.add('open')},
		close_menu:function(){options.classList.remove('open')},
	}

	tabs.forEach(function( tab ){
		tab.addEventListener('click',function( _event ){
			if(!this.classList.contains('current')){
				tabs.forEach(function(i){i.classList.remove('current')})
				this.classList.add('current');
				handlers[this.getAttribute('run')]();
			}
		})
	});
})(
	document.getElementById('js-mobile-menu'),
	document.getElementById('js-menu')
);


/* -----------------------------------------------------------------------------
	EYE TOGGLE

		This adds a 'click' eventlistener to the 'eye' in the menu
        that toggles the display of annotations in the article
*/
(function( eye ){
    if( eye ){
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
        eye.addEventListener('click',function(){
            if(this.classList.toggle('active-toggle')){
                annotations.enable();
                window.sessionStorage.setItem(this.id,true);
            } else {
                annotations.disable();
                window.sessionStorage.setItem(this.id,false);
            }
        });
    }
})(document.getElementById('eye-toggle'));

/* -----------------------------------------------------------------------------
	ANNOTATE ARTICLE

		This fetches and wraps annotations in the article.
*/
(function( target ){

	function annotate( element, values ){
		if(element.tagName!='A'){
			var content = '';
			for( var i = 0; i < element.childNodes.length; i++ ){
				var node = element.childNodes[i];
				switch( node.nodeType ){
					case 1:
						node.innerHTML = annotate( node, values );
						content += node.outerHTML;
						break;
					case 3:
                        var regex = new RegExp(values.join('|'),'g');
						content += node.nodeValue.replace(regex,function( value, index, text ){
							return '<span class="annotation" name="' + value + '">' + value + '</span>';
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
                values = response
                target.innerHTML = annotate( target, values );
                annotations.refresh();
            } catch(err){ console.log(err); }
        }
    }

    handle.open("GET", '/article/' + DATA.id + '/annotate', true);
    handle.send();
})(document.getElementById('js-article-content'));
