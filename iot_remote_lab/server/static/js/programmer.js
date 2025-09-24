// Initialize CodeMirror
const editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
    mode: 'text/x-c++src',
    theme: 'dracula',
    lineNumbers: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    lineWrapping: true,
    foldGutter: true,
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
    extraKeys: {
        "Ctrl-Space": "autocomplete",
        "Ctrl-S": function(cm) {
            saveProgram();
        }
    }
});

// Elements
const programNameInput = document.getElementById('program-name');
const saveBtn = document.getElementById('save-btn');
const loadBtn = document.getElementById('load-btn');
const loading = document.getElementById('loading');
const statusMessage = document.getElementById('status-message');
const statusText = document.getElementById('status-text');
const programsGrid = document.getElementById('programs-grid');

// Show status message
function showStatus(message, type = 'success') {
    statusText.textContent = message;
    statusMessage.className = `status-message ${type} show`;
    setTimeout(() => {
        statusMessage.classList.remove('show');
    }, 5000);
}

// Save program
async function saveProgram() {
    const programName = programNameInput.value.trim();
    const code = editor.getValue();

    if (!programName) {
        showStatus('Please enter a program name', 'error');
        programNameInput.focus();
        return;
    }

    if (!code.trim()) {
        showStatus('Please write some code before saving', 'error');
        editor.focus();
        return;
    }

    loading.classList.add('active');
    saveBtn.disabled = true;

    try {
        const response = await fetch('/api/save_program', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                program_name: programName,
                code: code,
                description: `C++ program created on ${new Date().toLocaleDateString()}`
            })
        });

        const data = await response.json();

        if (data.success) {
            showStatus(data.message, 'success');
            loadPrograms(); // Refresh the programs list
        } else {
            showStatus(data.error || 'Failed to save program', 'error');
        }
    } catch (error) {
        console.error('Error saving program:', error);
        showStatus('Network error: Failed to save program', 'error');
    } finally {
        loading.classList.remove('active');
        saveBtn.disabled = false;
    }
}

// Load program
async function loadProgram(programName) {
    try {
        const response = await fetch(`/api/load_program/${encodeURIComponent(programName)}`);
        const data = await response.json();

        if (data.success) {
            programNameInput.value = data.program_name;
            editor.setValue(data.code);
            showStatus(`Loaded program "${data.program_name}"`, 'success');
        } else {
            showStatus(data.error || 'Failed to load program', 'error');
        }
    } catch (error) {
        console.error('Error loading program:', error);
        showStatus('Network error: Failed to load program', 'error');
    }
}

// Load programs list
async function loadPrograms() {
    try {
        const response = await fetch('/api/list_programs');
        const data = await response.json();

        if (data.success) {
            displayPrograms(data.programs);
        } else {
            console.error('Failed to load programs:', data.error);
        }
    } catch (error) {
        console.error('Error loading programs:', error);
    }
}

// Display programs
function displayPrograms(programs) {
    programsGrid.innerHTML = '';

    if (programs.length === 0) {
        programsGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: var(--subtext1); padding: 2rem;">
                No saved programs yet. Create your first C++ program!
            </div>
        `;
        return;
    }

    programs.forEach(program => {
        const programCard = document.createElement('div');
        programCard.className = 'program-card';
        programCard.onclick = () => loadProgram(program.name);

        const createdDate = program.created_at 
            ? new Date(program.created_at).toLocaleDateString()
            : 'Unknown date';

        programCard.innerHTML = `
            <h4>📄 ${program.name}</h4>
            <div class="program-date">Created: ${createdDate}</div>
            ${program.description ? `<div class="program-description">${program.description}</div>` : ''}
        `;

        programsGrid.appendChild(programCard);
    });
}

// Event listeners
saveBtn.addEventListener('click', saveProgram);

// Load programs on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPrograms();
    editor.focus();
});

// Auto-save functionality (optional)
let autoSaveTimeout;
editor.on('change', () => {
    clearTimeout(autoSaveTimeout);
    // Uncomment to enable auto-save after 5 seconds of inactivity
    // autoSaveTimeout = setTimeout(() => {
    //     if (programNameInput.value.trim()) {
    //         saveProgram();
    //     }
    // }, 5000);
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveProgram();
    }
});