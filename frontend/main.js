// main.js
// -------
// All frontend logic lives here.
// Communicates with the FastAPI backend at http://localhost:8000
// Uses fetch() — no external libraries needed.

const API_BASE = "http://localhost:8000";

// --- TAB SWITCHING ---
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
        const tabName = e.target.dataset.tab;
        
        // Hide all tabs
        document.querySelectorAll(".tab-content").forEach(tab => {
            tab.classList.remove("active");
        });
        
        // Remove active from all buttons
        document.querySelectorAll(".tab-btn").forEach(b => {
            b.classList.remove("active");
        });
        
        // Show selected tab
        document.getElementById(tabName + "-tab").classList.add("active");
        e.target.classList.add("active");
    });
});

// --- PDF UPLOAD HANDLING ---
const pdfInput = document.getElementById("pdf-input");
const pdfLabel = document.getElementById("pdf-label");
const pdfFileDisplay = document.getElementById("pdf-file-display");
const pdfFilename = document.getElementById("pdf-filename");
const pdfRemoveBtn = document.getElementById("pdf-remove-btn");

pdfInput.addEventListener("change", (e) => {
    if (pdfInput.files.length > 0) {
        const filename = pdfInput.files[0].name;
        pdfFilename.textContent = filename;
        pdfLabel.style.display = "none";
        pdfFileDisplay.style.display = "flex";
    }
});

pdfRemoveBtn.addEventListener("click", (e) => {
    e.preventDefault();
    pdfInput.value = "";
    pdfLabel.style.display = "flex";
    pdfFileDisplay.style.display = "none";
    pdfFilename.textContent = "";
});

// --- COPY TO CLIPBOARD ---
// Attach this to every Copy button in the output cards
async function copyToClipboard(text, buttonElement) {
    try {
        await navigator.clipboard.writeText(text);
        buttonElement.textContent = "Copied!";
        setTimeout(() => buttonElement.textContent = "Copy", 2000);
    } catch (err) {
        alert("Failed to copy to clipboard");
    }
}

// --- GENERATE CONTENT ---
// Called when the user clicks the Generate button
document.getElementById("generate-btn").addEventListener("click", generateContent);
document.getElementById("generate-all-btn").addEventListener("click", generateAllContent);

async function generateAllContent() {
    // Check all format checkboxes
    document.querySelectorAll('input[name="format"]').forEach(checkbox => {
        checkbox.checked = true;
    });
    // Then generate
    await generateContent();
}

async function generateContent() {
    const activeTab = document.querySelector(".tab-btn.active").dataset.tab;
    const selectedFormats = getSelectedFormats();
    const tiktokType = document.getElementById("tiktok-type")?.value || "informative";
    const runBrandCheck = true; // Always run brand check now

    if (selectedFormats.length === 0) {
        return showError("Please select at least one format.");
    }

    // Show loading state
    setLoading(true);
    clearOutputs();

    try {
        let response;
        let basePayload = {
            tiktok_type: tiktokType,
            run_brand_check: runBrandCheck
        };

        if (activeTab === "text") {
            const text = document.getElementById("text-input").value.trim();
            if (!text) return showError("Please paste some article text first.");

            // Generate for each selected format
            for (const format of selectedFormats) {
                response = await fetch(`${API_BASE}/generate/text`, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        text,
                        format_type: format,
                        ...basePayload
                    })
                });
                
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || "Something went wrong.");
                }
                displayOutputs(data);
            }

        } else if (activeTab === "url") {
            const url = document.getElementById("url-input").value.trim();
            if (!url) return showError("Please enter a URL.");

            // Generate for each selected format
            for (const format of selectedFormats) {
                response = await fetch(`${API_BASE}/generate/url`, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        url,
                        format_type: format,
                        ...basePayload
                    })
                });
                
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || "Something went wrong.");
                }
                displayOutputs(data);
            }

        } else if (activeTab === "pdf") {
            const fileInput = document.getElementById("pdf-input");
            if (!fileInput.files.length) return showError("Please select a PDF file.");

            // Generate for each selected format
            for (const format of selectedFormats) {
                const formData = new FormData();
                formData.append("file", fileInput.files[0]);
                formData.append("format_type", format);
                formData.append("tiktok_type", tiktokType);
                formData.append("run_brand_check", runBrandCheck);

                response = await fetch(`${API_BASE}/generate/pdf`, {
                    method: "POST",
                    body: formData
                });
                
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || "Something went wrong.");
                }
                displayOutputs(data);
            }
        }

        // Reload history section
        loadHistory();

    } catch (err) {
        showError(err.message);
    } finally {
        setLoading(false);
    }
}

// Renders all output cards from the API response
function displayOutputs(data) {
    const outputSection = document.getElementById("output-section");
    // Only clear on the first response (when output section is showing placeholder)
    if (outputSection.querySelector(".output-placeholder")) {
        outputSection.innerHTML = "";
    }

    const formatLabels = {
        newsletter: "Governance Weekly Newsletter",
        linkedin: "LinkedIn Post",
        twitter: "Twitter / X Thread",
        tiktok: "TikTok Script",
        brand_check: "Brand Tone Check"
    };

    for (const [key, value] of Object.entries(data)) {
        const card = document.createElement("div");
        card.className = "output-card";

        // Brand check card gets special styling based on score
        if (key === "brand_check") {
            const score = extractBrandScore(value);
            const scoreClass = score >= 8 ? "score-green" : score >= 6 ? "score-yellow" : "score-red";
            card.classList.add("brand-card", scoreClass);
        }

        const copyBtn = document.createElement("button");
        copyBtn.className = "copy-btn";
        copyBtn.textContent = "Copy";

        card.innerHTML = `
            <div class="card-header">
                <h3>${formatLabels[key] || key}</h3>
            </div>
            <pre class="output-text">${escapeHtml(value)}</pre>
        `;

        // Append copy button and add event listener
        card.querySelector(".card-header").appendChild(copyBtn);
        copyBtn.addEventListener("click", () => {
            copyToClipboard(value, copyBtn);
        });

        outputSection.appendChild(card);
    }
}

// Helper: extracts numeric score from brand check text like "BRAND SCORE: 7/10"
function extractBrandScore(text) {
    const match = text.match(/BRAND SCORE:\s*(\d+)/i);
    return match ? parseInt(match[1]) : 5;
}

// Helper: prevents HTML injection in output text
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

// Loads and displays history from the backend
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/history?limit=20`);
        const data = await response.json();
        renderHistory(data.history);
    } catch (err) {
        console.error("Failed to load history:", err);
    }
}

// Renders the history list
function renderHistory(items) {
    const historyList = document.getElementById("history-list");
    
    if (!items || items.length === 0) {
        historyList.innerHTML = '<p class="history-empty">No generations yet</p>';
        return;
    }

    historyList.innerHTML = items.map(item => {
        const date = new Date(item.created_at).toLocaleString();
        const preview = item.output_text.substring(0, 100) + (item.output_text.length > 100 ? "..." : "");
        
        return `
            <div class="history-item" onclick="viewHistoryItem('${escapeHtml(item.output_text)}', '${item.format_type}')">
                <div class="history-item-info">
                    <div class="history-item-date">${date}</div>
                    <span class="history-item-format">${item.format_type.toUpperCase()}</span>
                    <div class="history-item-preview">${escapeHtml(preview)}</div>
                </div>
                <button class="delete-btn" onclick="deleteHistoryItem(${item.id}, event)">Delete</button>
            </div>
        `;
    }).join("");
}

// Deletes a history item
async function deleteHistoryItem(id, event) {
    event.preventDefault();
    try {
        await fetch(`${API_BASE}/history/${id}`, {method: "DELETE"});
        loadHistory();
    } catch (err) {
        alert("Failed to delete history item");
    }
}

// Views a history item - displays its content in the output section
function viewHistoryItem(content, formatType) {
    const outputSection = document.getElementById("output-section");
    outputSection.innerHTML = "";

    const formatLabels = {
        newsletter: "Governance Weekly Newsletter",
        linkedin: "LinkedIn Post",
        twitter: "Twitter / X Thread",
        tiktok: "TikTok Script",
        brand_check: "Brand Tone Check"
    };

    const card = document.createElement("div");
    card.className = "output-card";

    const copyBtn = document.createElement("button");
    copyBtn.className = "copy-btn";
    copyBtn.textContent = "Copy";

    card.innerHTML = `
        <div class="card-header">
            <h3>${formatLabels[formatType] || formatType}</h3>
        </div>
        <pre class="output-text">${escapeHtml(content)}</pre>
    `;

    card.querySelector(".card-header").appendChild(copyBtn);
    copyBtn.addEventListener("click", () => {
        copyToClipboard(content, copyBtn);
    });

    outputSection.appendChild(card);
}

// Show/hide loading spinner on the generate button
function setLoading(isLoading) {
    const btn = document.getElementById("generate-btn");
    const allBtn = document.getElementById("generate-all-btn");
    btn.disabled = isLoading;
    allBtn.disabled = isLoading;
    if (isLoading) {
        btn.textContent = "Generating...";
        allBtn.textContent = "Generating...";
    } else {
        btn.textContent = "Generate Content";
        allBtn.textContent = "All";
    }
}

function clearOutputs() {
    document.getElementById("output-section").innerHTML = "";
}

function showError(message) {
    const outputSection = document.getElementById("output-section");
    outputSection.innerHTML = `<div class="error-card">${escapeHtml(message)}</div>`;
}

function getSelectedFormats() {
    const checkboxes = document.querySelectorAll('input[name="format"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// --- HISTORY TOGGLE ---
// History is now in the sidebar, no toggle needed
// Just load history on page load

// Load history when page first opens
window.addEventListener("load", loadHistory);
