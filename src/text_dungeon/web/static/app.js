const output = document.getElementById("output");
const input = document.getElementById("command-input");
const form = document.getElementById("input-line");

const hpFill = document.getElementById("hp-fill");
const hpText = document.getElementById("hp-text");
const manaFill = document.getElementById("mana-fill");
const manaText = document.getElementById("mana-text");
const classText = document.getElementById("class-text");
const levelText = document.getElementById("level-text");
const xpText = document.getElementById("xp-text");
const dungeonText = document.getElementById("dungeon-text");
const mapDisplay = document.getElementById("map-display");
const equipmentList = document.getElementById("equipment-list");
const skillsList = document.getElementById("skills-list");
const inventoryList = document.getElementById("inventory-list");

const classSelect = document.getElementById("class-select");
const classOptions = document.getElementById("class-options");

const nameSelect = document.getElementById("name-select");
const nameForm = document.getElementById("name-form");
const nameInput = document.getElementById("name-input");

const playerNameText = document.getElementById("player-name-text");

const sidebar = document.getElementById("sidebar");
const sidebarBackdrop = document.getElementById("sidebar-backdrop");
const sidebarToggle = document.getElementById("sidebar-toggle");

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

function formatMapLines(lines) {
  const rows = lines.filter((line) => line !== "" && line !== "Map:");
  return rows.join("\n");
}

function renderStatus(status) {
  if (!status) return;

  const hpRatio = status.max_hp > 0 ? status.hp / status.max_hp : 0;
  hpFill.style.width = `${Math.max(0, Math.min(1, hpRatio)) * 100}%`;
  hpFill.classList.toggle("low", hpRatio <= 0.3);
  hpText.textContent = `${status.hp}/${status.max_hp}`;

  const manaRatio = status.max_mana > 0 ? status.mana / status.max_mana : 0;
  manaFill.style.width = `${Math.max(0, Math.min(1, manaRatio)) * 100}%`;
  manaText.textContent = `${status.mana}/${status.max_mana}`;

  playerNameText.textContent = status.name || "Adventurer";
  classText.textContent = status.player_class || "";
  levelText.textContent = status.level;
  xpText.textContent = `${status.xp}/${status.xp_per_level}`;
  dungeonText.textContent = `${status.dungeon_level}/${status.max_dungeon_level}`;

  mapDisplay.textContent = formatMapLines(status.map_lines) || "You haven't explored anywhere yet.";

  function itemRow(label, item) {
    const li = document.createElement("li");
    const name = document.createElement("span");
    name.className = "item-name";
    name.textContent = label ? `${label}: ${item ? item.name : "(empty)"}` : item.name;
    li.appendChild(name);
    if (item) {
      const desc = document.createElement("span");
      desc.className = "item-desc";
      desc.textContent = item.description;
      li.appendChild(desc);
    }
    return li;
  }

  equipmentList.innerHTML = "";
  equipmentList.appendChild(itemRow("Main hand", status.equipment.main_hand));
  equipmentList.appendChild(itemRow("Off hand", status.equipment.off_hand));

  function skillRow(skill) {
    const li = document.createElement("li");
    const name = document.createElement("span");
    name.className = "item-name";
    name.textContent = `${skill.name} (${skill.mana_cost} MP)`;
    li.appendChild(name);
    const desc = document.createElement("span");
    desc.className = "item-desc";
    desc.textContent = skill.description;
    li.appendChild(desc);
    return li;
  }

  skillsList.innerHTML = "";
  if (status.skills.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "No skills learned yet.";
    skillsList.appendChild(empty);
  } else {
    status.skills.forEach((skill) => {
      skillsList.appendChild(skillRow(skill));
    });
  }

  inventoryList.innerHTML = "";
  if (status.inventory.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "Nothing yet.";
    inventoryList.appendChild(empty);
  } else {
    status.inventory.forEach((item) => {
      inventoryList.appendChild(itemRow(null, item));
    });
  }
}

function showClassSelect(options, onChoose) {
  input.disabled = true;
  classOptions.innerHTML = "";
  options.forEach((option) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "class-option";
    const name = document.createElement("span");
    name.className = "class-option-name";
    name.textContent = option.name;
    const desc = document.createElement("span");
    desc.className = "class-option-desc";
    desc.textContent = option.description;
    button.appendChild(name);
    button.appendChild(desc);
    button.addEventListener("click", () => {
      onChoose(option.name);
      classSelect.classList.add("hidden");
      input.disabled = false;
      input.focus();
    });
    classOptions.appendChild(button);
  });
  classSelect.classList.remove("hidden");
}

function showNameSelect(defaultName, onChoose) {
  input.disabled = true;
  nameInput.value = "";
  nameInput.placeholder = defaultName;
  nameSelect.classList.remove("hidden");
  nameInput.focus();

  const handleSubmit = (event) => {
    event.preventDefault();
    const name = nameInput.value.trim();
    onChoose(name || defaultName);
    nameSelect.classList.add("hidden");
    nameForm.removeEventListener("submit", handleSubmit);
    input.disabled = false;
    input.focus();
  };
  nameForm.addEventListener("submit", handleSubmit);
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

function openSidebar() {
  sidebar.classList.add("open");
  sidebarBackdrop.classList.add("open");
}

function closeSidebar() {
  sidebar.classList.remove("open");
  sidebarBackdrop.classList.remove("open");
}

sidebarToggle.addEventListener("click", () => {
  if (sidebar.classList.contains("open")) {
    closeSidebar();
  } else {
    openSidebar();
  }
});
sidebarBackdrop.addEventListener("click", closeSidebar);

function connect() {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);

  socket.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "class_select") {
      showClassSelect(data.options, (chosenName) => socket.send(chosenName));
      return;
    }
    if (data.type === "name_select") {
      showNameSelect(data.default, (chosenName) => socket.send(chosenName));
      return;
    }
    appendLines(data.lines);
    renderStatus(data.status);
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
    closeSidebar();
  });
}

document.getElementById("terminal").addEventListener("click", (event) => {
  if (event.target === sidebarToggle) return;
  input.focus();
});

connect();
