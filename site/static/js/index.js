NodeList.prototype.forEach||(NodeList.prototype.forEach=function(e,t){for(var n=0,a=this.length;n<a;++n)e.call(t,this[n],n,this)}),function(e){function t(e){return e.id in sessionStorage?"false"!=sessionStorage.getItem(e.id):e.checked}for(var n=0;n<e.length;n++){var a=e[n];!function(e,n){for(var a=new Array,o=0;o<n.length;o++)a.push(n[o]);var r=new Array(e);r.push.apply(r,a),r.forEach(function(n){n&&(n.box=n.getElementsByTagName("input")[0],n.box.checked=t(n.box),n.classList.toggle("mark",n.box.checked),n==e?n.addEventListener("change",function(e){var t=this.box.checked;a.forEach(function(e){e.box.checked=t})}):n.addEventListener("change",function(t){e.box.checked=a.every(function(e){return e.box.checked})}),n.addEventListener("change",function(e){r.forEach(function(e){e.classList.toggle("mark",e.box.checked),window.sessionStorage.setItem(e.box.id,e.box.checked)})}))})}(a.getElementsByClassName("all")[0],a.getElementsByClassName("option"))}}(document.getElementsByClassName("drop-down-menu")),function(e){function t(t){t.preventDefault();for(var n=e.querySelectorAll(".categories .option>input[type=checkbox]"),a=e.querySelectorAll(".sources .option>input[type=checkbox]"),o=new Array,r=new Array,s=0;s<a.length;s++)(i=a[s]).checked&&r.push(i.getAttribute("no-name"));for(s=0;s<n.length;s++){var i=n[s];i.checked&&o.push(i.getAttribute("no-name"))}return document.getElementById("js-sources-str").value=r.join("|"),document.getElementById("js-categories-str").value=o.join("|"),e.submit(),!1}try{e.addEventListener("submit",t,!1)}catch(n){e.attachEvent("onsubmit",t)}}(document.getElementById("js-submit")),function(e){for(var t=0;t<e.length;t++){var n=e[t];n.id in sessionStorage?n.value=sessionStorage.getItem(n.id):sessionStorage.setItem(n.id,n.value),n.addEventListener("change",function(e){this.id&&sessionStorage.setItem(this.id,this.value)})}}(document.querySelectorAll('input[type="text"], input[type="number"], select')),function(e){e&&(e.innerHTML=(new Date).getFullYear())}(document.getElementById("js-year")),function(e){function t(){if(!s){s=!0,l+=1;var t=new XMLHttpRequest;t.onload=function(){if(200==this.status){for(var t=JSON.parse(this.responseText),a=0;a<t.length;a++){var o=t[a];astr='<div class="category">'+o.category_label+'</div><a class="title" href="/articles/'+o.id+'/" target="_blank">'+o.title+'</a><div class="date-source"><a class="source" href="'+o.link+'" target="_blank" rel="noopener">'+o.source_label+"</a> on "+o.fetched.split(" ")[0]+"</div>",aobj=document.createElement("div"),aobj.classList.add("titlecard"),aobj.innerHTML=astr,r.push(aobj)}n(l)}else{var d=document.createElement("div");d.classList.add("the-end"),d.innerHTML=c,e.appendChild(d),i=!0}s=!1},t.open("GET","/articles/?page="+l+"&next",!0),t.send()}}function n(e){var t={},n=window.location.search;n=n?-1==n.indexOf("page")?n.replace(/(\&+|\/+)$/,"")+"&page="+e:n.replace(/page=.*?(&|\/|$)/,"page="+e+"$1"):"?page="+e,history.replaceState(t,"page "+e,n)}function a(){if(!i){0==r.length&&t();var n=window.setInterval(function(){if(r.length>0){var t=r.shift();e.appendChild(t)}else window.clearInterval(n)},250)}}function o(){var e=window.pageYOffset+window.innerHeight;return document.body.offsetHeight-e}var r=[],s=!1,i=!1,c="no more articles here, sorry :/",l=window.location.search.match(/page=(.*?)(&|\/|$)/);l=null!=l?parseInt(l[1]):0,window.addEventListener("scroll",function(e){o()<100&&a()})}(document.getElementById("js-titlecard-list"));