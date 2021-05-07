var url = "ws://localhost:8765"

var ws = new WebSocket(url);

var inputTxt = document.getElementById("input");
var sendBtn = document.getElementById("sendMsg");
var connectMsg = document.getElementById("connection");
var outputP = document.getElementById("outputP");

ws.onopen = function (event) {
    connection.innerHTML = "connected";
}

function sendInput() {
    sendWs(inputTxt.value);
}

function sendWs(msg) {
    ws.send(msg);
}

ws.onmessage = function (event) {
    console.log(event.data);
    outputP.innerHTML = event.data;
}