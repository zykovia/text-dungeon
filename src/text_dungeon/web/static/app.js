const output = document.getElementById("output");
const input = document.getElementById("command-input");

function appendLine(text, className) {
  const div = document.createElement("div");
  div.textContent = text === "" ? " " : text;
  if (className) {
    div.className = className;
  }
  output.appendChild(div);
  output.scrollTop = output.scrollHeight;
}

function appendLines(lines) {
  lines.forEach((line) => appendLine(line));
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

  input.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") return;
    const command = input.value.trim();
    if (!command || socket.readyState !== WebSocket.OPEN) return;
    appendLine(`> ${command}`, "echo");
    socket.send(command);
    input.value = "";
  });
}

document.getElementById("terminal").addEventListener("click", () => input.focus());

connect();
