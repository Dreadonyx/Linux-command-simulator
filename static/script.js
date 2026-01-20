// Linux Command Simulator - Main Script

const output = document.getElementById("output");
const datetime = document.getElementById("datetime");

let currentPath = "/home/student";
let inputSpan = null;

// Update datetime in status bar
function updateDateTime() {
    const now = new Date();
    datetime.textContent = now.toLocaleString('en-US', {
        weekday: 'short',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}
updateDateTime();
setInterval(updateDateTime, 1000);

// Create a new prompt line
function createPromptLine() {
    const line = document.createElement("div");
    line.className = "line";

    const prompt = document.createElement("span");
    prompt.className = "prompt";
    prompt.textContent = `student@linux:${currentPath}$ `;

    inputSpan = document.createElement("span");
    inputSpan.className = "command";
    inputSpan.contentEditable = true;
    inputSpan.spellcheck = false;

    line.appendChild(prompt);
    line.appendChild(inputSpan);
    output.appendChild(line);

    placeCursorAtEnd(inputSpan);
}

// Place cursor at end of element
function placeCursorAtEnd(el) {
    el.focus();
    const range = document.createRange();
    range.selectNodeContents(el);
    range.collapse(false);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
}

// Initialize first prompt
createPromptLine();

// Handle keyboard input
document.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        const cmd = inputSpan.textContent.trim();
        if (!cmd) return;
        inputSpan.contentEditable = false;
        runCommand(cmd);
    }
});

// Execute command via backend
function runCommand(cmd) {
    fetch("/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd })
    })
        .then(res => res.json())
        .then(data => {
            if (data.path) {
                currentPath = data.path;
            }

            if (data.output === "__clear__") {
                output.innerHTML = "";
                createPromptLine();
                return;
            }

            if (data.output) {
                const out = document.createElement("div");
                out.className = "output";
                if (data.output.includes("not found") || data.output.includes("Error")) {
                    out.classList.add("error");
                }
                out.textContent = data.output;
                output.appendChild(out);
            }

            createPromptLine();
            window.scrollTo(0, document.body.scrollHeight);
        });
}
