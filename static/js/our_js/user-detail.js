function displayModal(btn) {
    let modal_id = btn.getAttribute('modal')
    let modal = $(`#${modal_id}`).toggle()
    let overlay = $("#my-overlay").toggle()
}

function closeModals(elm) {
    const modals = document.querySelectorAll('.my-modal');
    modals.forEach(modal => {
        modal.style.display = 'none'; 
    });
    elm.style.display = 'none'
}

$("#update-about").submit(function (e) {
    e.preventDefault();
    let modal = document.getElementById("profile-about-form-block")
    let form = document.getElementById("update-about")
    let csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value
    let about = $('#about-input').val();
    let profileID = $('#profile-id').val()
    let data = new FormData();
    data.append("about", about)


    $.ajax({
        type: "post",
        url: `/api/v1/profile/update/`,
        headers: {
            'Authorization': 'Token ' + localStorage.getItem('apiToken'),
            "X-CSRFToken": csrfToken
        },

        data: data,
        processData: false,
        contentType: false,
        success: function (response) {
            modal.style.display = 'None'
            $("#my-overlay").toggle()
            updateField('about', about)
            
        },
        error: function (response) {
            console.log(response)
        },
    });
});


$("#update-goals").submit(function (e) {
    e.preventDefault();
    let modal = document.getElementById("profile-goals-form-block")
    let form = document.getElementById("update-goals")
    let csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value
    let goals = $('#goals-input').val();
    let profileID = $('#profile-id').val()
    let data = new FormData();
    data.append("goals_for_life", goals)


    $.ajax({
        type: "post",
        url: `/api/v1/profile/update/`,
        headers: {
            'Authorization': 'Token ' + localStorage.getItem('apiToken'),
            "X-CSRFToken": csrfToken
        },

        data: data,
        processData: false,
        contentType: false,
        success: function (response) {
            modal.style.display = 'None'
            $("#my-overlay").toggle()
            updateField('goals', goals)
            
        },
        error: function (response) {
            console.log(response)
        },
    });
});

$("#update-interests").submit(function (e) {
    e.preventDefault();
    let modal = document.getElementById("profile-interests-form-block")
    let form = document.getElementById("update-interests")
    let csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value
    let interests = $('#interests-input').val();
    let profileID = $('#profile-id').val()
    let data = new FormData();
    data.append("interests", interests)


    $.ajax({
        type: "post",
        url: `/api/v1/profile/update/`,
        headers: {
            'Authorization': 'Token ' + localStorage.getItem('apiToken'),
            "X-CSRFToken": csrfToken
        },

        data: data,
        processData: false,
        contentType: false,
        success: function (response) {
            modal.style.display = 'None'
            $("#my-overlay").toggle()
            updateField('interests', interests)
            
        },
        error: function (response) {
            console.log(response)
        },
    });
});


function updateField(fieldName, text) {
    field_id = `user-${fieldName}-field`
    field = document.getElementById(field_id)
    field.innerText = text
}

function ProfileToSearchingInAllies(checkbox) {
    let csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value
    $.ajax({
        type: "post",
        url: `/api/v1/profile/to_searching_allies/`,
        headers: {
            'Authorization': 'Token ' + localStorage.getItem('apiToken'),
            "X-CSRFToken": csrfToken
        },
        processData: false,
        contentType: false,
        success: function (response) {
            
        },
        error: function (response) {
            console.log(response)
        },
    });
}