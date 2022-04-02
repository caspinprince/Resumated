// const updateScroll = () => {
//     $('#chat').scrollTop($('#chat')[0].scrollHeight);
// };

let socket;
$(document).ready(function () {
    socket = io('/chat')
    socket.on('connect', function () {
        socket.emit('joined', {});
    });
    socket.on('status', function (data) {
        console.log('changing')
        sessionStorage.setItem('username', data.username);
    });
    socket.on('message', function (data) {
        // console.log($('#chat').val() + data.msg + '\n')
        // $('#chat').val($('#chat').val() + data.msg + '\n');
        // $('#chat').scrollTop($('#chat')[0].scrollHeight);
        let username = sessionStorage.getItem('username')
        let chatbox = document.getElementById("chatbox")

        const isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop+1
        let lastGroup = chatbox.children[chatbox.children.length - 1].className
        lastGroup = lastGroup.includes("justify-content-end") ? "outgoing" : "incoming"
        let currentGroup = data.username === username ? "outgoing" : "incoming"
        let prev;
        if (currentGroup !== lastGroup || chatbox.children.length === 1) {
            prev = chatbox.children[chatbox.children.length - 1]
            let newGroup;
            if (currentGroup === "outgoing") {
                newGroup = $(`<div class="d-flex flex-row justify-content-end mb-4">
                            <div>
                                <p class="message-outgoing">${data.msg}</p>
                            </div>
                            <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava2-bg.webp"
                                 alt="avatar 1"
                                 style="width: 45px; height: 100%;">
                        </div>`)
            }
            else {
                newGroup = $(`<div class="d-flex flex-row justify-content-start mb-4">
                                <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava5-bg.webp"
                                 alt="avatar 1"
                                 style="width: 45px; height: 100%;">
                            <div>
                                <p class="message-incoming">${data.msg}</p>
                            </div>
                        </div>`);
            }
            $(prev).after(newGroup)
        } else {
            let msg = document.createElement('p');
            prev = currentGroup === "outgoing" ? chatbox.querySelectorAll(".message-outgoing") : chatbox.querySelectorAll(".message-incoming")
            msg.className = currentGroup === "outgoing" ? "message-outgoing" : "message-incoming"
            let text = document.createTextNode(data.msg);
            let last = prev[prev.length - 1]
            msg.appendChild(text);
            last.after(msg);
        }

        if (isScrolledToBottom) {
            console.log('should scroll')
            chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight
        }
    });
    $('#text').keypress(function (e) {
        var code = e.keyCode || e.which;
        if (code == 13) {
            text = $('#text').val();
            $('#text').val('');
            socket.emit('text', {msg: text});
        }
    });
});

function leave_room() {
    socket.emit('left', {}, function () {
        socket.disconnect();
    });
}