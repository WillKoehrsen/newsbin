function expand( element ){
    element.classList.toggle('active');
    var others = document.getElementsByClassName('active');
    for(var i = 0; i < others.length; i++ ){
        var item = others[i];
        if(item!=element){
            item.classList.remove('active');
        }
    }
}

function ancestor_has_class( element, _class ){
    while( element.parentNode && element.tagName!='HTML' ){
        if(element.classList.contains(_class)){
            return true;
        }
        element = element.parentNode;
    }
    return false;
}

window.addEventListener('click',function(_event){
    if(!ancestor_has_class(_event.target,'noclear')){
        var menus = document.getElementsByClassName('active');
        for(var i = 0; i < menus.length; i++ ){
            menus[i].classList.remove('active');
        }
    }
});
