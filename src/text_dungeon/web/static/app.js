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
const mapCanvas = document.getElementById("map-canvas");
const mapCanvasCtx = mapCanvas.getContext("2d");
const mapEmptyMessage = document.getElementById("map-empty-message");
const equipmentList = document.getElementById("equipment-list");
const skillsList = document.getElementById("skills-list");
const inventoryList = document.getElementById("inventory-list");

const worldSelect = document.getElementById("world-select");
const worldOptions = document.getElementById("world-options");

const classSelect = document.getElementById("class-select");
const classOptions = document.getElementById("class-options");

const nameSelect = document.getElementById("name-select");
const nameForm = document.getElementById("name-form");
const nameInput = document.getElementById("name-input");

const playerNameText = document.getElementById("player-name-text");

const sidebar = document.getElementById("sidebar");
const sidebarBackdrop = document.getElementById("sidebar-backdrop");
const sidebarToggle = document.getElementById("sidebar-toggle");

const TILE_SIZE = 16;
const TILE_SCALE = 2;

const FLOOR_VARIANTS = [
  "floor_1.png",
  "floor_2.png",
  "floor_3.png",
  "floor_4.png",
  "floor_5.png",
  "floor_6.png",
  "floor_7.png",
  "floor_8.png",
];
const STAIRS_TILE = "floor_stairs.png";
const WALL_TILE = "wall_mid.png";
const CHEST_ICON = "chest_full_open_anim_f0.png";
const FLASK_ICON = "flask_red.png";
const WEAPON_ICON = "weapon_rusty_sword.png";

const CLASS_SPRITES = {
  Warrior: "knight_m_idle_anim_f0.png",
  Ranger: "elf_m_idle_anim_f0.png",
  Cleric: "dwarf_m_idle_anim_f0.png",
  Wizard: "wizzard_m_idle_anim_f0.png",
};

const MONSTER_SPRITES = {
  skeleton: "skelet_idle_anim_f0.png",
  "giant rat": "wogol_idle_anim_f0.png",
  "cave spider": "chort_idle_anim_f0.png",
  shade: "muddy_anim_f0.png",
  "Dungeon Lord": "masked_orc_idle_anim_f0.png",
  "Dungeon Emperor": "big_demon_idle_anim_f0.png",
};

const HEAL_ITEM_NAMES = new Set(["health potion", "bandage"]);
const WIN_ITEM_NAME = "golden crown";

const SPRITE_FILES = [
  ...FLOOR_VARIANTS,
  STAIRS_TILE,
  WALL_TILE,
  CHEST_ICON,
  FLASK_ICON,
  WEAPON_ICON,
  ...Object.values(CLASS_SPRITES),
  ...Object.values(MONSTER_SPRITES),
];

let lastRoomsRendered = null;

const sprites = {};
SPRITE_FILES.forEach((file) => {
  const img = new Image();
  img.onload = () => renderMap(lastRoomsRendered);
  img.src = `/static/tiles/${file}`;
  sprites[file] = img;
});

function itemIconFor(itemName) {
  if (itemName === WIN_ITEM_NAME) return CHEST_ICON;
  if (HEAL_ITEM_NAMES.has(itemName)) return FLASK_ICON;
  return WEAPON_ICON;
}

// Deterministic pick so a given room always shows the same floor variant.
function floorVariantFor(roomId) {
  let hash = 0;
  for (let i = 0; i < roomId.length; i++) {
    hash = (hash + roomId.charCodeAt(i)) % FLOOR_VARIANTS.length;
  }
  return FLOOR_VARIANTS[hash];
}

function drawSprite(file, cellX, cellY) {
  const img = sprites[file];
  if (!img || !img.complete) return;
  const destSize = TILE_SIZE * TILE_SCALE;
  // Sprites narrower/wider than one tile get scaled to fit the tile's width,
  // keeping aspect ratio; taller sprites then overflow upward, so they're
  // anchored to the tile's bottom edge rather than its top.
  const drawWidth = destSize;
  const drawHeight = img.naturalWidth ? (img.naturalHeight / img.naturalWidth) * drawWidth : destSize;
  const dx = cellX * destSize;
  const dy = cellY * destSize + (destSize - drawHeight);
  mapCanvasCtx.drawImage(img, dx, dy, drawWidth, drawHeight);
}

function renderMap(rooms) {
  const roomIds = Object.keys(rooms || {});
  if (roomIds.length === 0) {
    mapCanvas.classList.add("hidden");
    mapEmptyMessage.classList.remove("hidden");
    return;
  }
  mapCanvas.classList.remove("hidden");
  mapEmptyMessage.classList.add("hidden");

  const xs = roomIds.map((id) => rooms[id].x);
  const ys = roomIds.map((id) => rooms[id].y);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const cols = maxX - minX + 1;
  const rows = maxY - minY + 1;
  const destTile = TILE_SIZE * TILE_SCALE;

  mapCanvas.width = cols * destTile;
  mapCanvas.height = rows * destTile;
  mapCanvasCtx.imageSmoothingEnabled = false;

  const roomAt = {};
  roomIds.forEach((id) => {
    roomAt[`${rooms[id].x},${rooms[id].y}`] = id;
  });

  for (let y = minY; y <= maxY; y++) {
    for (let x = minX; x <= maxX; x++) {
      const cellX = x - minX;
      // North (+y) is drawn at the top, matching the ASCII map's convention.
      const cellY = maxY - y;
      const roomId = roomAt[`${x},${y}`];
      if (roomId === undefined) {
        drawSprite(WALL_TILE, cellX, cellY);
        continue;
      }
      const room = rooms[roomId];
      drawSprite(room.auto_advance ? STAIRS_TILE : floorVariantFor(roomId), cellX, cellY);
      room.items.forEach((itemName) => drawSprite(itemIconFor(itemName), cellX, cellY));
      if (room.monster && MONSTER_SPRITES[room.monster]) {
        drawSprite(MONSTER_SPRITES[room.monster], cellX, cellY);
      }
      if (room.current) {
        const spriteFile = CLASS_SPRITES[currentPlayerClass];
        if (spriteFile) drawSprite(spriteFile, cellX, cellY);
      }
    }
  }
}

let currentPlayerClass = null;

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

  currentPlayerClass = status.player_class;
  lastRoomsRendered = status.rooms;
  renderMap(status.rooms);

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
      if (item.effect) {
        const effect = document.createElement("span");
        effect.className = "skill-effect";
        effect.textContent = item.effect;
        li.appendChild(effect);
      }
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
    const effect = document.createElement("span");
    effect.className = "skill-effect";
    effect.textContent = skill.effect;
    li.appendChild(effect);
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
  if (status.inventory.length === 0 && status.old_gear.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "Nothing yet.";
    inventoryList.appendChild(empty);
  } else {
    status.inventory.forEach((item) => {
      inventoryList.appendChild(itemRow(null, item));
    });
    if (status.old_gear.length > 0) {
      const li = document.createElement("li");
      const name = document.createElement("span");
      name.className = "item-name";
      name.textContent = `Old gear (${status.old_gear.length})`;
      li.appendChild(name);
      const desc = document.createElement("span");
      desc.className = "item-desc";
      desc.textContent = status.old_gear.join(", ");
      li.appendChild(desc);
      inventoryList.appendChild(li);
    }
  }
}

const LAST_WORLD_ID_KEY = "lastWorldId";

function characterSummaryText(character) {
  return (
    `${character.name} the ${character.player_class} — Level ${character.level}, ` +
    `Dungeon ${character.dungeon_level}/${character.max_dungeon_level}, ` +
    `HP ${character.hp}/${character.max_hp}, ${character.item_count} item(s)`
  );
}

function showWorldSelect(options, onChoose) {
  const remembered = localStorage.getItem(LAST_WORLD_ID_KEY);
  if (remembered && options.some((option) => option.id === remembered)) {
    onChoose(remembered);
    return;
  }

  input.disabled = true;
  worldOptions.innerHTML = "";
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
    if (option.character) {
      const character = document.createElement("span");
      character.className = "class-option-character";
      character.textContent = characterSummaryText(option.character);
      button.appendChild(character);
    }
    button.addEventListener("click", () => {
      onChoose(option.id);
      worldSelect.classList.add("hidden");
      input.disabled = false;
      input.focus();
    });
    worldOptions.appendChild(button);
  });
  worldSelect.classList.remove("hidden");
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
    if (data.type === "world_select") {
      showWorldSelect(data.options, (chosenId) => {
        localStorage.setItem(LAST_WORLD_ID_KEY, chosenId);
        socket.send(chosenId);
      });
      return;
    }
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
