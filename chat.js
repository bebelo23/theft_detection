const ws = new WebSocket("ws://172.20.10.4:8765");

ws.onopen = () => {
    console.log("Connected to the WebSocket server");
};

ws.onmessage = (event) => {
    const chatbox = document.getElementById("chatbox");
    const message = document.createElement("div");
    message.textContent = event.data;
    chatbox.appendChild(message);
};

function sendMessage() {
    const input = document.getElementById("message");
    ws.send(input.value);
    input.value = "";
}
