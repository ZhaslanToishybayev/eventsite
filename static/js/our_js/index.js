let $logoutBtn = document.getElementById('logout-btn');
if ($logoutBtn)
{
    $logoutBtn.addEventListener('click', function(event) {
        localStorage.removeItem('apiToken');
    });
}