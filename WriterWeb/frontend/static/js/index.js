window.onload = async function(){
    await loadDOMUrls();

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

async function loadDOMUrls(){
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken',document.querySelector('#csrf-subform input').value);
    const response = await fetch(
        '/router/home', 
        {
            method:"POST", 
            body:formData
        }
    );
    if (await response.redirected){
        window.location.href= await response.url
    } else {
        jres = await response.json();
        headersRes = await fetch(
            jres['urlheader']
        )
        headerhtml = await headersRes.text();
        document.getElementById('header').innerHTML= headerhtml;

        leftsRes = await fetch(
            jres['urlleft']
        )
        lefthtml = await leftsRes.text();
        document.getElementById('tools-blog').innerHTML= lefthtml;

        mainsRes = await fetch(
            jres['urlmain']
        )
        mainhtml = await mainsRes.text();
        document.getElementById('main-content').innerHTML= mainhtml;

        rightsRes = await fetch(
            jres['urlright']
        )
        rightshtml = await rightsRes.text();
        document.getElementById('quick-acess').innerHTML= rightshtml;
    }
}