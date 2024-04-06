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
    token = document.getElementById("login-form").querySelector('input').value
    username = document.getElementById("login-username").value;
    password = document.getElementById("login-password").value;
    repass = document.getElementById("login-password").value;
}
