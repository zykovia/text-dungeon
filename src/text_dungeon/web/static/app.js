const output = document.getElementById("output");
const input = document.getElementById("command-input");
const form = document.getElementById("input-line");

function appendLine(text, className) {
  const div = document.createElement("div");
  div.textContent = text === "" ? " " : text;
  if (className) {
    div.className = className;
  }
  output.appendChild(div);
  output.scrollTop = output.scrollHeight;
}

function appendLines(lines) {
  lines.forEach((line) => appendLine(line));
}

// Tracks the real visible viewport (excluding an open on-screen keyboard) so
// the input line stays visible instead of being pushed off-screen or hidden
// behind the keyboard on mobile browsers.
function setAppHeight() {
  const height = window.visualViewport ? window.visualViewport.height : window.innerHeight;
  document.documentElement.style.setProperty("--app-height", `${height}px`);
}
setAppHeight();
window.addEventListener("resize", setAppHeight);
if (window.visualViewport) {
  window.visualViewport.addEventListener("resize", setAppHeight);
  window.visualViewport.addEventListener("scroll", setAppHeight);
}

function connect() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  socket.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    appendLines(data.lines);
    if (data.game_over) {
      appendLine("");
      appendLine("--- refresh the page to play again ---", "echo");
      input.disabled = true;
    }
  });

  socket.addEventListener("close", () => {
    appendLine("");
    appendLine("--- connection closed. refresh to reconnect ---", "echo");
    input.disabled = true;
  });

  socket.addEventListener("error", () => {
    socket.close();
  });

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const command = input.value.trim();
    if (!command || socket.readyState !== WebSocket.OPEN) return;
    appendLine(`> ${command}`, "echo");
    socket.send(command);
    input.value = "";
    input.focus();
  });
}

document.getElementById("terminal").addEventListener("click", () => input.focus());

connect();
