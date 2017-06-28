
/* -----------------------------------------------------------------------------
	TOOLTIPS

		This immediately invoked function adds event listeners that create
        and destroy tooltips on elements with the 'tooltip="<message>"'
        attribute/value. They have the following features.

        1.  all tooltips have the class 'tooltip'

        2.  tooltips are oriented relative to the target element

        3.  if the left side of the target element is to the right of
            the viewport center, then the tooltip will be on the left,
            otherwise it will default to the right.
*/
var tooltips = (function( targets ){
    // function that actually adds the tooltip
    function make_tooltip( element ){
            var tooltip = null;
            var offset = 10;

            element.addEventListener('mouseover',function( _event ){
                var popup = document.createElement('div');
                tooltip = popup;
                popup.classList.add("tooltip");
                var msg = _event.target.getAttribute('tooltip');
                if(msg){
                    popup.innerHTML = msg;
                    document.body.appendChild(popup);

                    // move to where the tooltip should display
                    var reference = _event.target.getBoundingClientRect();
                    var right_ref = parseInt(reference.right);
                    var left_ref = parseInt(reference.left);

                    if(left_ref < window.innerWidth/2){
                        popup.style.left = right_ref+window.pageXOffset+offset+'px'
                        popup.classList.add('left');
                    }
                    else {
                        popup.style.left = left_ref-parseInt(popup.offsetWidth)+window.pageXOffset-offset+'px'
                        popup.classList.add('right');
                    }

                    popup.style.top = parseInt(reference.top) + window.pageYOffset + 'px';
                }
            });

            element.addEventListener('mouseout',function( _event ){
                if(tooltip && tooltip.parentNode){
                    tooltip.parentNode.removeChild(tooltip);
                }
                tooltip = null;
            });
    }

    // handler
    handler = {
        add:function( item ){
            if(item.hasAttribute('tooltip')){
                make_tooltip( item );
            }
        }
    }

    targets.forEach(function( target ){
        make_tooltip( target );
    });

    return handler;
})([...document.querySelectorAll('[tooltip]')]);

/*
(function( item ){
    item.addEventListener('click',function( _event ){
        if(sessionStorage.length > 0){
            console.log('items in session');
            _event.preventDefault();
        }
    });
})(document.getElementById('js-check-submit'));
*/
