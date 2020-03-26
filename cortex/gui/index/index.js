var api_host = '127.0.0.1';
var api_port = '5000';

function openUserMenu() {
    $("#userList").empty()
    fetch(`http://${api_host}:${api_port}/users`)
      .then(response => response.json())
      .then(users => createUserList(users));
    $("#usersMenu").css("width", "15%");
}

function openSnapshotMenu(event) {
    $("#snapshotList").empty()
    fetch(`http://${api_host}:${api_port}/users/${event.data.uid}/snapshots`)
        .then(response => response.json())
        .then(snapshots => createSnapshotList(snapshots));
    $("#snapshotMenu").css("width", "15%");
}

function closeSideMenu() {
    $(this).parent().css("width", "0");
}

function createUserList(users) {
    for (let i = 0; i < users.length; i++) {
        let user = users[i];
        $("#userList").append(`<li class="userNode">${user["name"]}</li>`)
        $("#userList li").eq(i).click({uid: user["uid"]}, openSnapshotMenu)
    }
}

function createSnapshotList(uid, snapshots) {
    for (let i = 0; i < snapshots.length; i++) {
        let snapshot = snapshots[i];
        $("#snapshotList").append(`<li class="snapshotNode">${snapshot["datetime"]}</li>`)
        $("#snapshotList li").eq(i).click({uid: uid, sid: snapshot["id"]}, getSnapshot)
    }
}

function getSnapshot(uid, sid) {

}

$(document).ready(function() {
  $("#usersBtn").click(openUserMenu);
  $(".closebtn").click(closeSideMenu);
});
