window.onload = async function(){
    await loadDOMUrls(false);
    document.getElementById('to-personal-page').addEventListener('click', async function() {await loadDom('personalpage'); });

    document.getElementById('logout-button').addEventListener('click', async function(){
        const token = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', token);
        document.getElementById("logout-button").innerHTML='<span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span role="status">In process</span>'
        const checkingJson = await checklogout(formData, token);
        if (checkingJson['Err']) {
            document.getElementById('logout-status').innerHTML = checkingJson['detail'];
        } else {
            fetch(checkingJson['url'],
                {
                    method: 'DELETE',
                    headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': token
                },
                body: formData
            }).then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            }).catch(function(err) {
                document.getElementById('logout-status').innerHTML = err;
            });
        }
    })

    document.addEventListener('click', function(event) {
        var optionsMenu = document.querySelectorAll('.options-menu');
        
        optionsMenu.forEach(function(element){
            elementButton = element.previousElementSibling;
            if(event.target != element && event.target.parentNode != element && event.target != elementButton && event.target.parentNode != elementButton){
                element.style.display = 'none';
            }
        });
    });
}

async function checklogout(formData, token) {
    const response = await fetch('/check/login', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': token
        },
        body: formData
    })
    return await response.json();
}

function toggleOptions(menuID) {
    var optionsMenu = document.getElementById(menuID);
    optionsMenu.style.display = (optionsMenu.style.display === 'block') ? 'none' : 'block';
}

async function loadDOMUrls(onlymain){
    changeLink('link-home')
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken',document.querySelector('#csrf-subform input').value);
    let response = await fetch(
        '/router/home', 
        {
            method:"POST", 
            body:formData
        }
    );
    if (response.redirected){
        window.location.href= response.url
    } else {
        jres = await response.json();
        if (!onlymain){
            headersRes = await fetch(
                jres['urlheader']
            )
            headerhtml = await headersRes.text();
            document.getElementById('header').classList.remove('show');
            document.getElementById('header').innerHTML= headerhtml;
            setTimeout(function(){
                document.getElementById('header').classList.add('show');
            }, 500)

            leftsRes = await fetch(
                jres['urlleft']
            )
            lefthtml = await leftsRes.text();
            document.getElementById('tools-blog').classList.remove('show');
            document.getElementById('tools-blog').innerHTML= lefthtml;
            setTimeout(function(){
                document.getElementById('tools-blog').classList.add('show');
            }, 500);
            rightsRes = await fetch(
                jres['urlright']
            )
            rightshtml = await rightsRes.text();
            document.getElementById('quick-acess').classList.remove('show');
            document.getElementById('quick-acess').innerHTML= rightshtml;
            setTimeout(function(){
                document.getElementById('quick-acess').classList.add('show');
            }, 500);
        }else await loadDOMUrlsRight();
        mainsRes = await fetch(
            jres['urlmain']
        )
        mainhtml = await mainsRes.text();
        document.getElementById('main-content').classList.remove('show');
        document.getElementById('main-content').innerHTML= mainhtml;
        setTimeout(function(){
            document.getElementById('main-content').classList.add('show');
        }, 500)
    }
}

async function loadDOMUrlsRight(){
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken',document.querySelector('#csrf-subform input').value);
    let response = await fetch(
        '/router/home', 
        {
            method:"POST", 
            body:formData
        }
    );
    if (response.redirected){
        window.location.href= response.url
    } else {
        jres = await response.json();
        rightsRes = await fetch(
            jres['urlright']
        )
        rightshtml = await rightsRes.text();
        document.getElementById('quick-acess').classList.remove('show');
        document.getElementById('quick-acess').innerHTML= rightshtml;
        setTimeout(function(){
            document.getElementById('quick-acess').classList.add('show');
        }, 500);
    }
}

async function loadDom(route){
    if(route == 'personalpage'){
        await loadDOMUrlsRight();
        changeLink('link-people');
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken',document.querySelector('#csrf-subform input').value);
        const response = await fetch(
            '/router/personal', 
            {
                method:"POST", 
                body:formData
            }
        );
        if (response.redirected){
            window.location.href= response.url
        }else{
            jres=await response.json();
            document.getElementById('main-content').classList.remove('show');
            mainsRes = await fetch(
                jres['urlmain']
            )
            mainhtml = await mainsRes.text();
            document.getElementById('main-content').innerHTML=mainhtml;
            setTimeout(function (){
                document.getElementById('main-content').classList.add('show');
            }, 500);
            document.getElementById('personal-feed-nav').addEventListener('click',async function() {await loadDom("personalpage")} );
            document.getElementById('personal-info-nav').addEventListener('click',async function() {await loadDom("personalinfo")} );
        }
    }
    if(route == 'personalinfo'){
        document.getElementById('personal-feed-nav').classList.remove('now-link');
        document.getElementById('personal-info-nav').classList.add('now-link');
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken',document.querySelector('#csrf-subform input').value);
        const response = await fetch(
            '/router/personalinfo', 
            {
                method:"POST", 
                body:formData
            }
        );
        if (response.redirected){
            window.location.href= response.url
        }else{
            document.getElementById('personal-main-content').innerHTML = await response.text();
        }
    }
    if(route == 'friends'){
        await loadDOMUrlsRight();
        changeLink('link-people');
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken',document.querySelector('#csrf-subform input').value);
        const response = await fetch(
            '/router/friends', 
            {
                method:"POST", 
                body:formData
            }
        );
        document.getElementById('main-content').classList.remove('show');
        document.getElementById('main-content').innerHTML=await response.text();
        setTimeout(function (){
            document.getElementById('main-content').classList.add('show');
        }, 500);
    }
    if (route == 'universes'){
        await loadDOMUrlsRight();
        changeLink('link-universe');
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken',document.querySelector('#csrf-subform input').value);
        const response = await fetch(
            '/router/universes', 
            {
                method:"POST", 
                body:formData
            }
        );
        document.getElementById('main-content').classList.remove('show');
        document.getElementById('main-content').innerHTML=await response.text();
        setTimeout(function (){
            document.getElementById('main-content').classList.add('show');
        }, 500);
    }
}

async function read(chapterid){
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken',document.querySelector('#csrf-subform input').value);
    const response = await fetch(
        '/router/readview@' + chapterid, 
    );
    let responsejson = await response.json();
    document.getElementById('main-content').classList.remove('show');
    document.getElementById('main-content').innerHTML=responsejson['mainhtml'];
    setTimeout(function (){
        document.getElementById('main-content').classList.add('show');
    }, 500);
    document.getElementById('quick-acess').classList.remove('show');
    document.getElementById('quick-acess').innerHTML=responsejson['righthtml'];
    var blogs = document.querySelectorAll(".comments-blog");
    for (var i = 1; i < blogs.length; i++) {
        var marginTopValue = parseInt(getComputedStyle(blogs[i - 1]).marginTop, 10) + 100;
        blogs[i].style.marginTop = marginTopValue + "px";
    }
    document.addEventListener("click", function(event){
        var chapterDropdown = document.getElementById("chapter-dropdown");
        var nowChapterButton = document.querySelector("#now-chapter-show button");

        if(event.target != chapterDropdown && event.target.parentNode != chapterDropdown && event.target != nowChapterButton && event.target.parentNode != nowChapterButton){
            chapterDropdown.style.display = "none";
        }
    });
    setTimeout(function (){
        document.getElementById('quick-acess').classList.add('show');
    }, 500);
}

function toggleDropdownChapter(){
    var chapterDropdown = document.getElementById("chapter-dropdown");
    chapterDropdown.style.display = (chapterDropdown.style.display === "block") ? "none" : "block";
}

function changeLink(link){
    let links = document.getElementsByClassName('nav-link');
    [...links].forEach(element => {
        element.classList.remove('now-link');
    });

    let targetElement = document.getElementById(link);
    if (targetElement) {
        targetElement.classList.add('now-link');
    }
}
