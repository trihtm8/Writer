window.onload = async function(){
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