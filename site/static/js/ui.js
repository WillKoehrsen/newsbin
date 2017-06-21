var tooltips = (function( targets ){
    // function that actually adds the tooltip
    function make_tooltip( element ){
            var tooltip = null;
            var offset = 10;

            element.addEventListener('mouseover',function( _event ){
                var popup = document.createElement('div');
                tooltip = popup;
                popup.classList.add("tooltip");
                popup.innerHTML = element.getAttribute('tooltip');
                document.body.appendChild(popup);

                // move to where the tooltip should display
                var reference = element.getBoundingClientRect();
                var right_ref = parseInt(reference.right);
                var left_ref = parseInt(reference.left);

                if(left_ref < window.innerWidth/2){
                    popup.style.left = right_ref+offset+'px'
                    popup.classList.add('left');
                }
                else {
                    popup.style.left = left_ref-parseInt(popup.offsetWidth)-offset+'px'
                    popup.classList.add('right');
                }

                popup.style.top = parseInt(reference.top) + 'px';
            });

            element.addEventListener('mouseout',function( _event ){
                if(tooltip){
                    tooltip.parentNode.removeChild(tooltip);
                }
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
