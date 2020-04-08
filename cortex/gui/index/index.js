var api_host = '127.0.0.1';
var api_port = '5000';

function openUserNav() {
    $(".userNode").remove()
    fetch(`http://${api_host}:${api_port}/users`)
        .then(response => response.json())
        .then(function(users) {
            // Create the user list
            for (let i = 0; i < users.length; i++) {
                let user = users[i];
                $("#userNav").append(`<a href="#" class="userNode">${user["name"]}</a>`)
                $("#userNav").children().eq(i+1).click({uid: user["uid"]}, openSnapshotNav)
            }
        });
    $("#userNav").css("width", "15%");
}

function openSnapshotNav(event) {
    $(".snapshotNode").remove()
    fetch(`http://${api_host}:${api_port}/users/${event.data.uid}/snapshots`)
        .then(response => response.json())
        .then(function(snapshots) {
            // Create the snapshot list
            for (let i = 0; i < snapshots.length; i++) {
                let snapshot = snapshots[i];
                $("#snapshotNav").append(`<a href="#" class="snapshotNode">${snapshot["datetime"]}</a>`)
                $("#snapshotNav").children().eq(i+1).click({uid: event.data.uid, sid: snapshot["id"]}, openSnapshot)
            }
        });
    $("#snapshotNav").css("width", "15%");
}

function openSnapshot(event) {
    fetch(`http://${api_host}:${api_port}/users/${event.data.uid}`)
        .then(response => response.json())
        .then(function(user) {
            // Fill the user information
            $('#user #name .value').text(user["name"])
            if (user['gender'] == 'm') {
                $('#user #name i').removeClass("fa-female")
                $('#user #name i').addClass("fa-male")
            } else {
                $('#user #name i').removeClass("fa-male")
                $('#user #name i').addClass("fa-female")
            }
            $('#user #birthday .value').text(user['birthday'])
        });

    fetch(`http://${api_host}:${api_port}/users/${event.data.uid}/snapshots/${event.data.sid}`)
        .then(response => response.json())
        .then(function(snapshot) {
            $.each(snapshot['fields'], function(i, field){
                fillSnapshotResult(event.data.uid, event.data.sid, field)
            });
        });
    $('#snapshot').css('visibility', 'visible')
}

function fillSnapshotResult(uid, sid, field) {
    fetch(`http://${api_host}:${api_port}/users/${uid}/snapshots/${sid}/${field}`)
        .then(response => response.json())
        .then(function(result) {
            switch(field) {
                case 'pose':
                    break;
                case 'feelings':
                    $('#feelings #hunger .value').text(result['hunger'].toFixed(3))
                    $('#feelings #thirst .value').text(result['thirst'].toFixed(3))
                    $('#feelings #exhaustion .value').text(result['exhaustion'].toFixed(3))
                    $('#feelings #happiness .value').text(result['happiness'].toFixed(3))
                case 'image_color':
                    $('#snapshot').css('background-image', 'url(' + result[field] + ')')
                    break;
                case 'image_depth':
                    break;
            }
        });
}

function closeSideNav() {
    $(this).parent().css("width", "0");
}

$(document).ready(function() {
  $("#usersBtn").click(openUserNav);
  $(".closebtn").click(closeSideNav);
});
