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
						refs.data.innerHTML += '<div class="modal-data-item">\
													<div>'+item.key+'</div>\
													<div>'+item.value+'</div>\
												</div>';
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
var annotations = (function( annotations ){
	if(annotations){
        var active = true;

		for( var i = 0; i < annotations.length; i++ ){
			annotations[i].addEventListener("click", function(_event){
				if(active){ modal.open(this.getAttribute('name')); }
			});
		}

        var handlers = {
            disable:function(){
                active = false;
                for( var i = 0; i < annotations.length; i++ ){
                    annotations[i].classList.remove('highlight');
        		}
            },
            enable:function(){
                active = true;
                for( var i = 0; i < annotations.length; i++ ){
                    annotations[i].classList.add('highlight');
        		}
            },
        }
        handlers.enable();
        return handlers;
	}
})(document.getElementsByClassName('annotation'));

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
	document.getElementById('js-capture-selection'),
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
