const chatbox = document.getElementById("chatbox")

$(document).ready(function () {
    const isScrolledToBottom = chatbox.scrollHeight - chatbox.clientHeight <= chatbox.scrollTop + 1

    if (isScrolledToBottom) {
        chatbox.scrollTop = chatbox.scrollHeight - chatbox.clientHeight
    }
});