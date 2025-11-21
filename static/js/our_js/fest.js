let baseURL = "/api/v1/festivals"

let btn = $('#FestivalParticipationRequest')
    btn.click(function (e) {
    let club = $('#selectedClub').val();
    let festival = $('#festivalId').val();
    let festResponseElm = $('#festResponseText');
    festResponseElm.removeClass('text-danger', 'text-success')

    $.ajax({
        url: `${baseURL}/${festival}/festival_action/`,
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        headers: {
            'Authorization': 'Token ' + localStorage.getItem('apiToken'),
        },
        data: JSON.stringify({
            "action": "join",
            "club": club,
        }),
        success: function (response) {
            console.log(response)
            festResponseElm.innerText = ''
            festResponseElm.html('Запрос отправлен').addClass('text-success')
            // $('.close-button').click();
        },
        error: function(response, status){
            console.log(response, status)
            let festErrorsElm = document.getElementById('festResponseText')
            festResponseElm.innerText = ''
            festResponseElm.html(response.responseJSON.detail).addClass('text-danger')
        }
    })
});