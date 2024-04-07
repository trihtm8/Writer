setTimeout (
    async function(){
        await document.getElementById('first-forms').classList.remove('show');
}, 500);
document.getElementById('first-forms').style.display='none';
document.getElementById('more-info-register-forms').classList.add('show');
document.getElementById('register-penname').value=document.getElementById('register-username').value.toUpperCase();

async function nextform(){
    document.getElementById('more-info-register-form1').classList.remove('show');
    await document.getElementById('more-info-register-form1').classList.add('hidden');
    document.getElementById('more-info-register-form2').classList.remove('hidden');
    setTimeout (
        async function(){
            await document.getElementById('more-info-register-form2').classList.add('show');
    }, 50);
}

async function prevform(){
    document.getElementById('more-info-register-form2').classList.remove('show');
    await document.getElementById('more-info-register-form2').classList.add('hidden');
    document.getElementById('more-info-register-form1').classList.remove('hidden');
    setTimeout (
        async function(){
            await document.getElementById('more-info-register-form1').classList.add('show');
    }, 50);
}

document.getElementById('more-info-register-form1').addEventListener('submit', async function(event){
    event.preventDefault();
    await nextform();
})

document.getElementById('prevform').addEventListener('click',async function(){
    await prevform();
})

document.getElementById('cancel').addEventListener('click', function(){
    window.location="/";
})

document.getElementById('more-info-register-form2').addEventListener('submit',async function(event){
    event.preventDefault();
    token = document.querySelector('#more-info-register-form2 input').value;
    username = document.getElementById('register-username').value;
    password = document.getElementById('register-password').value;
    repass = document.getElementById('register-repass').value;
    email = document.getElementById('register-email').value;
    first_name = document.getElementById('register-firstname').value;
    last_name = document.getElementById('register-lastname').value;
    company = document.getElementById('register-company').value;
    pen_name = document.getElementById('register-penname').value;
    profile_name = document.getElementById('register-profilename').value;
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', token);
    formData.append('username', username);
    formData.append('password', password);
    formData.append('repass', repass);
    formData.append('email', email);
    formData.append('first_name', first_name);
    formData.append('last_name', last_name);
    formData.append('company', company);
    formData.append('pen_name', pen_name);
    formData.append('profile_name', profile_name)
    response = await fetch(
        '/backend/888/register',
        {
            method: 'POST',
            body: formData
        }
    )
    if (await response.redirected) {
        window.location.href = response.url;
    }
})