function ApproveFestivalRequest(btn) {
    let csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value
    let requestID = btn.getAttribute('request-id')
    $.ajax({
        type: "post",
        url: `/api/v1/festival/join_requests/${requestID}/request_action/`,
        data: {
            "action": "approve",
        },
        headers: {
            'Authorization': 'Token ' + localStorage.getItem('apiToken'),
            "X-CSRFToken": csrfToken
        },
        success: function (response) {
            console.log(response)
            let requestStatusStr = document.getElementById(`request-status-${requestID}`)
            requestStatusStr.innerText = 'Принят'
            requestStatusStr.className = 'request_status d-block font-weight-bold';
            requestStatusStr.classList.add('text-success')
        },
        error: function (response) {
            console.log(response)
        },
    });
}

function RejectFestivalRequest(btn) {
    let csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value
    let requestID = btn.getAttribute('request-id')
    $.ajax({
        type: "post",
        url: `/api/v1/festival/join_requests/${requestID}/request_action/`,
        data: {
            "action": "reject",
        },
        headers: {
            'Authorization': 'Token ' + localStorage.getItem('apiToken'),
            "X-CSRFToken": csrfToken
        },
        success: function (response) {
            console.log(response)
            let requestStatusStr = document.getElementById(`request-status-${requestID}`)
            requestStatusStr.innerText = 'Отклонен'
            requestStatusStr.className = 'request_status d-block font-weight-bold';
            requestStatusStr.classList.add('text-danger')
        },
        error: function (response) {
            console.log(response)
        },
    });
}

function DeleteClubFromFestival(btn) {
    let csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value
    let requestID = btn.getAttribute('request-id')
    $.ajax({
        type: "post",
        url: `/api/v1/festival/join_requests/${requestID}/request_action/`,
        data: {
            "action": "reject",
        },
        headers: {
            'Authorization': 'Token ' + localStorage.getItem('apiToken'),
            "X-CSRFToken": csrfToken
        },
        success: function (response) {
            console.log(response)
            let requestStatusStr = document.getElementById(`request-status-${requestID}`)
            requestStatusStr.innerText = 'Клуб удален, вы можете заново принять его на странице запросов'
            requestStatusStr.className = 'request_status d-block font-weight-bold text-center';
            requestStatusStr.classList.add('text-danger')
        },
        error: function (response) {
            console.log(response)
        },
    });
}


31
78
53
50
63
69
65
55
40
60
45