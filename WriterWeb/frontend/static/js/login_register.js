window.onload = function(){
    document.getElementById("loading-spinner").innerHTML="";
    document.getElementById("openLoginformButton").addEventListener('click', async function(){
        document.getElementById("register-form").classList.remove("show");
        document.getElementById("login-form").classList.add("show");
    })
    
    document.getElementById("openRegisterformButton").addEventListener('click', async function(){
        document.getElementById("login-form").classList.remove("show");
        document.getElementById("register-form").classList.add("show");
    })

    document.getElementById("login-form").onload = setTimeout(function(){
        document.getElementById("login-form").classList.add("show");
    }, 500)

    document.getElementById("login-form").addEventListener('submit', async function(event){
        event.preventDefault();
        document.getElementById("login-submit").innerHTML='<span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span role="status">In process</span>'
        checkingJson = await checklogin();
        if (checkingJson['err']){
            document.getElementById("login-form-status").innerHTML=checkingJson['detail']
            document.getElementById("login-submit").innerHTML='Login';
        }
        else{
            this.action=checkingJson['loginUrl'];
            this.method=checkingJson['method'];
            this.submit();
        }
    })

    document.getElementById('register-form').addEventListener('submit', async function(event){
        event.preventDefault();
        document.getElementById("register-submit").innerHTML='<span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span role="status">In process</span>'
        checkingJson = await checkRegister();
        console.log(checkingJson);
        if (checkingJson['err']){
            document.getElementById('register-status').innerHTML=checkingJson['detail'];
            document.getElementById("register-submit").innerHTML='Register'
        }else{
            document.getElementById('more-info-register-forms').innerHTML=checkingJson['html'];
            var script = document.createElement('script');
            script.src = checkingJson['scriptUrl'];
            script.async = true;
            document.head.appendChild(script);
        }
    })
}

async function checklogin(){
    token = document.getElementById("login-form").querySelector('input').value
    username = document.getElementById("login-username").value;
    password = document.getElementById("login-password").value;
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', token);
    formData.append('username', username);
    formData.append('password', password);
    const response = await fetch('/check/login', {
        method: 'POST',
        body: formData
    })
    return await response.json();
}

async function checkRegister(){
    token = document.getElementById("register-form").querySelector('input').value
    username = document.getElementById("register-username").value;
    password = document.getElementById("register-password").value;
    repass = document.getElementById("register-repass").value;
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', token);
    formData.append('username', username);
    formData.append('password', password);
    formData.append('repass', repass);
    const response = await fetch('/check/register', {
        method: 'POST',
        body: formData
    })
    responsetext = await response.text();
    if (responsetext.charAt(0) == '{'){
        returnJson = JSON.parse(responsetext);
    }else {
        var startIndex = responsetext.indexOf('<');
        scriptUrl = responsetext.substring(0, startIndex);
        html = responsetext.substring(startIndex);
        returnJson = {
            'err' : false,
            'html' : html,
            'scriptUrl' : scriptUrl.replace(/\n/g, '')
        }
    }
    return returnJson;
}
