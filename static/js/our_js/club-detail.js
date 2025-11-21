function likeClub(btn) {
    let action_data = {
        'action': 'like'
    }
    let club_id = btn.getAttribute("club_id")
    $.ajax({
        type: "post",
        url: `/api/v1/clubs/${club_id}/club_action/`,
        data: action_data,
        headers: {'Authorization': 'Token ' + localStorage.getItem('apiToken')},
        success: function (response) {
            let likeClubBtn = document.getElementById('like-club-btn');
            likeClubBtn.setAttribute('onclick', 'dislikeClub(this)')
            let like_icon = document.getElementById('like-icon');
            like_icon.classList.remove('fa-regular');
            like_icon.classList.add('fa-solid')
            let likes_count = document.getElementById('likes_count')
            likes_count.innerText = parseInt(likes_count.innerText) + 1
        },
        error: function(response) {
            console.log(response.status)
            let currentURL = window.location.pathname
            console.log(currentURL)
            if (response.status == 401) {
                window.location.href = `/accounts/login/?next=${currentURL}`
            }
        }
    });
}

function dislikeClub(btn) {
    let action_data = {
        'action': 'unlike'
    }
    let club_id = btn.getAttribute("club_id")
    $.ajax({
        type: "post",
        url: `/api/v1/clubs/${club_id}/club_action/`,
        data: action_data,
        headers: {'Authorization': 'Token ' + localStorage.getItem('apiToken')},
        success: function (response) {
            let likeClubBtn = document.getElementById('like-club-btn');
            likeClubBtn.setAttribute('onclick', 'likeClub(this)')
            let like_icon = document.getElementById('like-icon');
            like_icon.classList.remove('fa-solid');
            like_icon.classList.add('fa-regular')
            let likes_count = document.getElementById('likes_count')
            likes_count.innerText = parseInt(likes_count.innerText) - 1
            
        },
        error: function(response) {
            let currentURL = window.location.pathname
            if (response.status == 401) {
                window.location.href = `/accounts/login/?next=${currentURL}`
            }
        }
    });
}


function joinClub(btn) {
    let action_data = {
        'action': 'join'
    }
    let club_id = btn.getAttribute("club_id")
    let wa_link = btn.getAttribute("wa")
    $.ajax({
        type: "post",
        url: `/api/v1/clubs/${club_id}/club_action/`,
        data: action_data,
        headers: {'Authorization': 'Token ' + localStorage.getItem('apiToken')},
        success: function (response) {
            let joinClubBtn = document.getElementById('join-club-btn');
            joinClubBtn.setAttribute('onclick', 'leaveClub(this)')
            let join_icon = document.getElementById('join-icon');
            join_icon.classList.remove('fa-arrow-right-to-bracket');
            join_icon.classList.add('fa-right-from-bracket')
            let members_count = document.getElementById('members_count')
            members_count.innerText = parseInt(members_count.innerText) + 1
            let join_btn = document.getElementById('join-btn-text')
            join_btn.innerText = 'Покинуть'
            joinClubBtn.classList.remove('btn-success')
            joinClubBtn.classList.add('btn-danger')
            if (wa_link!=="None")
                window.open(wa_link, '_blank');
        },
        error: function(response) {
            console.log(response)
            let currentURL = window.location.pathname
            if (response.status == 401) {
                window.location.href = `/accounts/login/?next=${currentURL}`
            }
        }
    });
}


function leaveClub(btn) {
    let action_data = {
        'action': 'leave'
    }
    let club_id = btn.getAttribute("club_id")
    $.ajax({
        type: "post",
        url: `/api/v1/clubs/${club_id}/club_action/`,
        data: action_data,
        headers: {'Authorization': 'Token ' + localStorage.getItem('apiToken')},
        success: function (response) {
            let joinClubBtn = document.getElementById('join-club-btn');
            joinClubBtn.setAttribute('onclick', 'joinClub(this)')
            let join_icon = document.getElementById('join-icon');
            join_icon.classList.remove('fa-right-from-bracket');
            join_icon.classList.add('fa-arrow-right-to-bracket')
            let members_count = document.getElementById('members_count')
            members_count.innerText = parseInt(members_count.innerText) - 1
            let join_btn = document.getElementById('join-btn-text')
            join_btn.innerText = 'Вступить'
            joinClubBtn.classList.remove('btn-danger')
            joinClubBtn.classList.add('btn-success')
        },
        error: function(response) {
            console.log(response)
            let currentURL = window.location.pathname
            if (response.status == 401) {
                window.location.href = `/accounts/login/?next=${currentURL}`
            }
        }
    });
}