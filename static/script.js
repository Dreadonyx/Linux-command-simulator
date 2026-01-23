// Linux Command Simulator - Main Script

const output = document.getElementById("output");
const datetime = document.getElementById("datetime");

let currentPath = "/home/student";
let inputSpan = null;

// Command history
let commandHistory = [];
let historyIndex = -1;

// Nano editor state
let nanoMode = false;
let nanoFilename = "";
let nanoTextarea = null;
let nanoOverlay = null;
let nanoSaveMode = false; // When prompting for filename

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

    // Add zero-width space to prevent span collapse
    inputSpan.innerHTML = '\u200B';

    line.appendChild(prompt);
    line.appendChild(inputSpan);
    output.appendChild(line);

    // Reset history index when new prompt is created
    historyIndex = commandHistory.length;

    // Prevent span from becoming completely empty (cursor would fall down)
    inputSpan.addEventListener('input', function () {
        if (this.textContent === '' || this.innerHTML === '' || this.innerHTML === '<br>') {
            this.innerHTML = '\u200B';
            placeCursorAtEnd(this);
        }
    });

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

// Create nano editor overlay
function openNano(filename, content) {
    nanoMode = true;
    nanoFilename = filename;
    nanoSaveMode = false;

    // Create overlay
    nanoOverlay = document.createElement("div");
    nanoOverlay.className = "nano-overlay";
    nanoOverlay.innerHTML = `
        <div class="nano-editor">
            <div class="nano-header">
                <span class="nano-title">  GNU nano 6.2</span>
                <span class="nano-filename" id="nano-filename-display">${filename}</span>
                <span class="nano-modified" id="nano-modified"></span>
            </div>
            <textarea class="nano-content" id="nano-textarea" spellcheck="false">${escapeHtml(content)}</textarea>
            <div class="nano-footer" id="nano-footer">
                <div class="nano-shortcuts">
                    <span><span class="nano-key">^G</span> Help</span>
                    <span><span class="nano-key">^O</span> Write Out</span>
                    <span><span class="nano-key">^W</span> Where Is</span>
                    <span><span class="nano-key">^K</span> Cut</span>
                    <span><span class="nano-key">^J</span> Justify</span>
                    <span><span class="nano-key">^C</span> Location</span>
                </div>
                <div class="nano-shortcuts">
                    <span><span class="nano-key">^X</span> Exit</span>
                    <span><span class="nano-key">^R</span> Read File</span>
                    <span><span class="nano-key">^\\</span> Replace</span>
                    <span><span class="nano-key">^U</span> Paste</span>
                    <span><span class="nano-key">^T</span> Execute</span>
                    <span><span class="nano-key">^_</span> Go To Line</span>
                </div>
            </div>
            <div class="nano-status" id="nano-status"></div>
        </div>
    `;
    document.body.appendChild(nanoOverlay);

    nanoTextarea = document.getElementById("nano-textarea");
    nanoTextarea.focus();

    // Track modifications
    nanoTextarea.addEventListener("input", () => {
        document.getElementById("nano-modified").textContent = " Modified";
    });
}

// Escape HTML for safe display
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Close nano editor
function closeNano() {
    if (nanoOverlay) {
        document.body.removeChild(nanoOverlay);
        nanoOverlay = null;
        nanoTextarea = null;
        nanoMode = false;
        nanoSaveMode = false;
        nanoFilename = "";
        createPromptLine();
    }
}

// Show save prompt (like real nano)
function showSavePrompt() {
    nanoSaveMode = true;
    const footer = document.getElementById("nano-footer");
    footer.innerHTML = `
        <div class="nano-save-prompt">
            <span>File Name to Write: </span>
            <input type="text" id="nano-filename-input" value="${nanoFilename}" spellcheck="false" />
        </div>
        <div class="nano-shortcuts">
            <span><span class="nano-key">^G</span> Help</span>
            <span><span class="nano-key">^C</span> Cancel</span>
        </div>
    `;
    const filenameInput = document.getElementById("nano-filename-input");
    filenameInput.focus();
    filenameInput.select();
}

// Hide save prompt and restore normal footer
function hideSavePrompt() {
    nanoSaveMode = false;
    const footer = document.getElementById("nano-footer");
    footer.innerHTML = `
        <div class="nano-shortcuts">
            <span><span class="nano-key">^G</span> Help</span>
            <span><span class="nano-key">^O</span> Write Out</span>
            <span><span class="nano-key">^W</span> Where Is</span>
            <span><span class="nano-key">^K</span> Cut</span>
            <span><span class="nano-key">^J</span> Justify</span>
            <span><span class="nano-key">^C</span> Location</span>
        </div>
        <div class="nano-shortcuts">
            <span><span class="nano-key">^X</span> Exit</span>
            <span><span class="nano-key">^R</span> Read File</span>
            <span><span class="nano-key">^\\</span> Replace</span>
            <span><span class="nano-key">^U</span> Paste</span>
            <span><span class="nano-key">^T</span> Execute</span>
            <span><span class="nano-key">^_</span> Go To Line</span>
        </div>
    `;
    nanoTextarea.focus();
}

// Save file via backend
function saveNanoFile(filename, content, callback) {
    fetch("/nano/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename, content })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                nanoFilename = filename;
                document.getElementById("nano-filename-display").textContent = filename;
                showNanoStatus(`[ Wrote ${content.split('\n').length} lines ]`);
                document.getElementById("nano-modified").textContent = "";
                if (callback) callback(true);
            } else {
                showNanoStatus(`[ Error: ${data.error} ]`);
                if (callback) callback(false);
            }
        });
}

// Show status message in nano
function showNanoStatus(message) {
    const status = document.getElementById("nano-status");
    if (status) {
        status.textContent = message;
        setTimeout(() => { status.textContent = ""; }, 2000);
    }
}

// Initialize first prompt
createPromptLine();

// Handle keyboard input
document.addEventListener("keydown", function (e) {
    // Nano mode keyboard handling
    if (nanoMode) {
        // Handle save prompt mode
        if (nanoSaveMode) {
            if (e.key === "Enter") {
                e.preventDefault();
                const filenameInput = document.getElementById("nano-filename-input");
                const filename = filenameInput.value.trim();
                if (filename) {
                    const content = nanoTextarea.value;
                    saveNanoFile(filename, content, () => {
                        hideSavePrompt();
                    });
                }
            } else if (e.ctrlKey && (e.key === "c" || e.key === "C")) {
                e.preventDefault();
                hideSavePrompt();
            } else if (e.ctrlKey && (e.key === "g" || e.key === "G")) {
                e.preventDefault();
                showNanoStatus("Enter filename and press Enter to save, ^C to cancel");
            }
            return;
        }

        // Normal nano mode
        if (e.ctrlKey) {
            if (e.key === "x" || e.key === "X") {
                e.preventDefault();
                const modified = document.getElementById("nano-modified").textContent;
                if (modified) {
                    // Ask to save
                    showNanoStatus("Save modified buffer? (Y)es, (N)o, (C)ancel");
                    const saveHandler = (evt) => {
                        evt.preventDefault();
                        if (evt.key.toLowerCase() === "y") {
                            const content = nanoTextarea.value;
                            saveNanoFile(nanoFilename, content, () => {
                                closeNano();
                            });
                        } else if (evt.key.toLowerCase() === "n") {
                            closeNano();
                        } else if (evt.key.toLowerCase() === "c" || evt.key === "Escape") {
                            showNanoStatus("");
                            nanoTextarea.focus();
                        }
                        document.removeEventListener("keydown", saveHandler);
                    };
                    document.addEventListener("keydown", saveHandler);
                } else {
                    closeNano();
                }
            } else if (e.key === "o" || e.key === "O") {
                e.preventDefault();
                showSavePrompt();
            } else if (e.key === "g" || e.key === "G") {
                e.preventDefault();
                showNanoStatus("Help: ^X Exit | ^O Save | ^K Cut line | ^U Paste | ^W Search");
            } else if (e.key === "k" || e.key === "K") {
                e.preventDefault();
                // Cut current line
                const textarea = nanoTextarea;
                const start = textarea.selectionStart;
                const value = textarea.value;
                const lineStart = value.lastIndexOf('\n', start - 1) + 1;
                const lineEnd = value.indexOf('\n', start);
                const end = lineEnd === -1 ? value.length : lineEnd + 1;
                const cutText = value.substring(lineStart, end);
                navigator.clipboard.writeText(cutText);
                textarea.value = value.substring(0, lineStart) + value.substring(end);
                textarea.selectionStart = textarea.selectionEnd = lineStart;
                document.getElementById("nano-modified").textContent = " Modified";
                showNanoStatus("[ Cut 1 line ]");
            } else if (e.key === "u" || e.key === "U") {
                e.preventDefault();
                // Paste from clipboard
                navigator.clipboard.readText().then(text => {
                    const textarea = nanoTextarea;
                    const start = textarea.selectionStart;
                    const end = textarea.selectionEnd;
                    textarea.value = textarea.value.substring(0, start) + text + textarea.value.substring(end);
                    textarea.selectionStart = textarea.selectionEnd = start + text.length;
                    document.getElementById("nano-modified").textContent = " Modified";
                });
            } else if (e.key === "w" || e.key === "W") {
                e.preventDefault();
                const searchTerm = prompt("Search:");
                if (searchTerm) {
                    const textarea = nanoTextarea;
                    const index = textarea.value.indexOf(searchTerm, textarea.selectionEnd);
                    if (index !== -1) {
                        textarea.selectionStart = index;
                        textarea.selectionEnd = index + searchTerm.length;
                        textarea.focus();
                    } else {
                        showNanoStatus(`[ "${searchTerm}" not found ]`);
                    }
                }
            } else if (e.key === "c" || e.key === "C") {
                e.preventDefault();
                // Show cursor position
                const textarea = nanoTextarea;
                const pos = textarea.selectionStart;
                const lines = textarea.value.substring(0, pos).split('\n');
                const line = lines.length;
                const col = lines[lines.length - 1].length + 1;
                showNanoStatus(`[ line ${line}, col ${col} ]`);
            }
        }
        return;
    }

    // Normal terminal mode
    if (e.key === "Enter") {
        e.preventDefault();
        // Strip zero-width space character used to prevent cursor drop
        const cmd = inputSpan.textContent.replace(/\u200B/g, '').trim();
        if (!cmd) return;

        // Add to history
        if (cmd && (commandHistory.length === 0 || commandHistory[commandHistory.length - 1] !== cmd)) {
            commandHistory.push(cmd);
        }

        inputSpan.contentEditable = false;
        runCommand(cmd);
    } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (commandHistory.length > 0 && historyIndex > 0) {
            historyIndex--;
            inputSpan.textContent = commandHistory[historyIndex];
            placeCursorAtEnd(inputSpan);
        }
    } else if (e.key === "ArrowDown") {
        e.preventDefault();
        if (historyIndex < commandHistory.length - 1) {
            historyIndex++;
            inputSpan.textContent = commandHistory[historyIndex];
            placeCursorAtEnd(inputSpan);
        } else if (historyIndex === commandHistory.length - 1) {
            historyIndex = commandHistory.length;
            inputSpan.textContent = "";
        }
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

            // Check for nano mode
            if (data.output && data.output.startsWith("__nano__:")) {
                const parts = data.output.split(":");
                const filename = parts[1];
                const content = parts.slice(2).join(":");
                openNano(filename, content);
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
