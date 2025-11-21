let RegisterURL = "/api/v1/register/";
let RegisterVerifyURL = "/api/v1/verify/";
let LoginURL = "/api/v1/token/";

jQuery("#register_user_form").submit(function (e) {
    e.preventDefault();
    formData = new FormData(jQuery(this)[0]);
    form_id = this.id;
    let csrfToken = formData.get("csrfmiddlewaretoken");
    const phone = formData.get("phone"); // Получаем значение телефона

    // Список допустимых префиксов
    const validPrefixes = [
        '+770', '+7747', '+7771', '+7775', '+7776', '+7777', '+7778'
    ];

    // Проверка номера телефона
    const isValidPhone = validPrefixes.some(prefix => phone.startsWith(prefix));

    if (!isValidPhone) {
        insertFieldErrors('phone', "Номер телефона должен начинаться на один из следующих префиксов: " + validPrefixes.join(", "))
        return; // Останавливаем отправку формы, если номер невалиден
    }

    formData.delete("csrfmiddlewaretoken");

    clearFieldErrors();
    jQuery.ajax({
        type: "post",
        url: RegisterURL,
        headers: {
            "X-CSRFToken": csrfToken,
        },
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            localStorage.setItem("session_id", response.session_id);
            localStorage.setItem("email", response.email);
            swapForm(form_id, response.email);
        },
        error: function (response) {
            console.log(response);
            insertAllErrors(response.responseJSON);
        },
    });
});

jQuery("#verify_user_form").submit(function (e) {
    e.preventDefault();
    formData = new FormData(jQuery(this)[0]);
    let csrfToken = formData.get("csrfmiddlewaretoken");
    let code_input = $("#id_email_code").val();
    let data = {
        user_session_id: localStorage.getItem("session_id"),
        email_code: code_input,
    };

    clearFieldErrors();
    jQuery.ajax({
        type: "post",
        url: RegisterVerifyURL,
        headers: {
            "X-CSRFToken": csrfToken,
        },
        data: JSON.stringify(data),
        processData: false,
        contentType: "application/json;charset=utf-8",
        success: function (response) {
            localStorage.setItem("apiToken", response.token);
            localStorage.removeItem("session_id");
            localStorage.removeItem("email_code");
            localStorage.removeItem("phone");
            localStorage.removeItem("email");
            document.location.href = "/";
        },
        error: function (response) {
            console.log(response.responseJSON);
            insertAllErrors(response.responseJSON);
        },
    });
});

function insertAllErrors(errors) {
    for (let field_name in errors) {
        insertFieldErrors(field_name, errors[field_name]);
    }
}

function insertFieldErrors(field_name, errors) {
    let blockErrors;
    if (field_name == "password") {
        blockErrors = document.getElementById(`errors_password2`);
        if (!blockErrors) {
            blockErrors = document.getElementById("errors_password");
        }
    } else {
        blockErrors = document.getElementById(`errors_${field_name}`);
    }
    if (typeof errors === "string") {
        let errorElm = `<p class='text-danger text-center'>${errors}</p>`;
        blockErrors.innerHTML += errorElm;
    } else {
        for (let i = 0; i < errors.length; i++) {
            let errorElm = `<p class='text-danger text-center'>${errors[i]}</p>`;
            blockErrors.innerHTML += errorElm;
        }
    }
}

function clearFieldErrors() {
    let errorBlocks = document.getElementsByClassName("block-errors");
    for (let errorBlock of errorBlocks) {
        errorBlock.innerHTML = "";
    }
}

function swapForm(form_id, email) {
    let verifyMessageElm = document.getElementById("verify-message");

    let formVerify = document.getElementById("verify_user_form");
    let form = document.getElementById(form_id);
    form.style.display = "none";
    formVerify.style.display = "block";
    let formTitle = document.getElementById("form-title");
    formTitle.innerText = "Введите код из почты";
    verifyMessageElm.innerText = `Мы отправили его на ${email}`;
}
