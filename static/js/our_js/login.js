$('#login_user_form').submit(function (e) {
    e.preventDefault();
    let login_form = document.getElementById("login_user_form") ;
    let login = $("#id_username").val();
    let password = $("#id_password2").val();
    $.ajax({
        type: "post",
        url: `/api/v1/login/`,
        data: JSON.stringify({username: login, password: password}),
        dataType: 'json',
        contentType: 'application/json',
        success: function (response) {
            localStorage.setItem('apiToken', response.token);
            login_form.submit();
        },
        error: function(response, status){console.log(response, status);}
    });
    }
);
