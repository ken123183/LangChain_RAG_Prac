document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "/api/v1";
    
    // UI Elements
    const apiKeyInput = document.getElementById("api-key");
    const demoPasswordInput = document.getElementById("demo-password");
    const saveKeyBtn = document.getElementById("save-key-btn");
    const verifyDemoBtn = document.getElementById("verify-demo-btn");
    const authStatus = document.getElementById("auth-status");
    
    const fileUpload = document.getElementById("file-upload");
    const dropzone = document.getElementById("dropzone");
    const fileNameDisplay = document.getElementById("file-name-display");
    const uploadBtn = document.getElementById("upload-btn");
    const uploadStatus = document.getElementById("upload-status");
    const resetVaultBtn = document.getElementById("reset-vault-btn");
    
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const chatMessages = document.getElementById("chat-messages");

    // Viewer Elements
    const docViewer = document.getElementById("doc-viewer");
    const docContent = document.getElementById("doc-content");
    const currentDocTitle = document.getElementById("current-doc-title");
    const toggleViewerBtn = document.getElementById("toggle-viewer-btn");
    const closeViewerBtn = document.getElementById("close-viewer");

    // UI Feedback Logic
    function updateAuthUI(state) {
        authStatus.className = "status-indicator";
        if (state === 'success') {
            authStatus.classList.add("unlocked");
            saveKeyBtn.textContent = "Vault Secured";
            saveKeyBtn.style.background = "var(--success)";
            if(verifyDemoBtn) verifyDemoBtn.textContent = "Verified";
        } else if (state === 'error') {
            authStatus.style.background = "var(--error)";
            saveKeyBtn.textContent = "Try Again";
            saveKeyBtn.style.background = "var(--error)";
            if(verifyDemoBtn) verifyDemoBtn.textContent = "Retry";
        } else {
            authStatus.classList.add("locked");
            saveKeyBtn.textContent = "Apply API Key";
            saveKeyBtn.style.background = "var(--primary)";
            if(verifyDemoBtn) verifyDemoBtn.textContent = "Unlock";
        }
    }

    // Viewer Logic
    function toggleViewer(show = null) {
        if (show === null) docViewer.classList.toggle("collapsed");
        else if (show) docViewer.classList.remove("collapsed");
        else docViewer.classList.add("collapsed");
    }

    async function fetchAndDisplayContent(filename) {
        try {
            const response = await fetch(`${API_URL}/documents/view?filename=${filename}`);
            if (response.ok) {
                const data = await response.json();
                currentDocTitle.textContent = filename;
                docContent.textContent = data.content;
                toggleViewer(true);
            }
        } catch (error) {
            console.error("Failed to fetch doc content", error);
        }
    }

    // Event Listeners for Viewer
    toggleViewerBtn.addEventListener("click", () => toggleViewer());
    closeViewerBtn.addEventListener("click", () => toggleViewer(false));

    // Reset Knowledge logic
    resetVaultBtn.addEventListener("click", async () => {
        if (!confirm("⚠️ 確定要清空目前的知識庫嗎？這將會刪除所有已載入的文件記憶。")) return;
        
        resetVaultBtn.disabled = true;
        uploadStatus.textContent = "⏳ 正在清空知識庫...";
        
        try {
            const response = await fetch(`${API_URL}/documents/reset`, { method: "POST" });
            if (response.ok) {
                uploadStatus.textContent = "🗑️ 知識庫已清空";
                uploadStatus.style.color = "var(--success)";
                chatMessages.innerHTML = ""; // Clear chat
                docContent.textContent = "知識庫已重置。請重新載入文檔以開始。";
                currentDocTitle.textContent = "No Document Loaded";
                toggleViewer(false);
            } else {
                uploadStatus.textContent = "❌ 清空失敗";
                uploadStatus.style.color = "var(--error)";
            }
        } catch (error) {
            uploadStatus.textContent = "❌ 連線錯誤";
        } finally {
            resetVaultBtn.disabled = false;
        }
    });

    // Verify Credentials
    async function verifyCredentials(apiKey = "", password = "") {
        try {
            const response = await fetch(`${API_URL}/auth/verify`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ api_key: apiKey, password: password })
            });
            if (response.ok) {
                updateAuthUI('success');
                return true;
            } else {
                updateAuthUI('error');
                return false;
            }
        } catch (error) {
            updateAuthUI('error');
            return false;
        }
    }

    // Initialize from LocalStorage
    const savedKey = localStorage.getItem("google_api_key");
    if (savedKey) {
        apiKeyInput.value = savedKey;
        updateAuthUI('success');
    }

    saveKeyBtn.addEventListener("click", () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            verifyCredentials(key, "").then(isValid => {
                if (isValid) localStorage.setItem("google_api_key", key);
            });
        }
    });

    verifyDemoBtn.addEventListener("click", () => {
        const password = demoPasswordInput.value.trim();
        if (password) verifyCredentials("", password);
    });

    // Handle credentials for requests
    const getCredentials = () => {
        const apiKey = apiKeyInput.value.trim() || localStorage.getItem("google_api_key") || "";
        const password = demoPasswordInput.value.trim() || "";
        if (!apiKey && !password) {
            alert("🔒 請先驗證身分以解鎖知識庫。");
            return null;
        }
        return { apiKey, password };
    };

    // Sample Loading logic
    document.querySelectorAll(".sample-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const filename = btn.getAttribute("data-file");
            const credentials = getCredentials();
            if (!credentials) return;

            uploadStatus.textContent = `⏳ 正在同步雲端知識: ${filename}...`;
            uploadStatus.style.color = "var(--primary)";
            btn.disabled = true;

            try {
                const response = await fetch(`${API_URL}/documents/load-local`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ filename, api_key: credentials.apiKey, password: credentials.password })
                });

                if (response.ok) {
                    uploadStatus.textContent = `✅ 知識同步完成！`;
                    uploadStatus.style.color = "var(--success)";
                    fetchAndDisplayContent(filename);
                } else {
                    const error = await response.json();
                    uploadStatus.textContent = `❌ 載入失敗: ${error.detail}`;
                    uploadStatus.style.color = "var(--error)";
                }
            } catch (error) {
                uploadStatus.textContent = "❌ 連線錯誤";
            } finally {
                btn.disabled = false;
            }
        });
    });

    // File Upload Handling
    dropzone.addEventListener("click", () => fileUpload.click());
    fileUpload.addEventListener("change", (e) => {
        if (e.target.files.length > 0) fileNameDisplay.textContent = e.target.files[0].name;
    });

    uploadBtn.addEventListener("click", async () => {
        const file = fileUpload.files[0];
        if (!file) {
            uploadStatus.textContent = "❌ 請選擇檔案";
            return;
        }
        
        const credentials = getCredentials();
        if (!credentials) return;

        uploadStatus.textContent = "⏳ 正在注入知識庫...";
        uploadBtn.disabled = true;

        const formData = new FormData();
        formData.append("file", file);
        formData.append("api_key", credentials.apiKey);
        formData.append("password", credentials.password);

        try {
            const response = await fetch(`${API_URL}/documents/upload`, {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                uploadStatus.textContent = "✅ 知識同步完成！";
                await fetchAndDisplayContent(file.name);
            } else {
                const error = await response.json();
                uploadStatus.textContent = `❌ 失敗: ${error.detail}`;
            }
        } catch (error) {
            uploadStatus.textContent = "❌ 連線錯誤";
        } finally {
            uploadBtn.disabled = false;
        }
    });

    // Chat Logic
    function appendMessage(role, content, sources = []) {
        const container = document.createElement("div");
        container.className = `msg-container ${role}`;
        let sourcesHtml = "";
        if (sources && sources.length > 0) {
            const uniqueSources = {};
            sources.forEach(s => {
                const key = `${s.source}_${s.page || 'none'}`;
                if (!uniqueSources[key]) uniqueSources[key] = s;
            });

            sourcesHtml = `<div class="source-box"><strong>📚 來源引用:</strong><br>${Object.values(uniqueSources).map(s => {
                const pageInfo = s.page ? ` (第 ${s.page} 頁)` : "";
                const sourceName = s.source.split(/[\\/]/).pop();
                return `• ${sourceName}${pageInfo}: ${s.content.substring(0, 60)}...`;
            }).join("<br>")}</div>`;
        }
        container.innerHTML = `<div class="msg-bubble">${content.replace(/\n/g, '<br>')}${sourcesHtml}</div>`;
        chatMessages.appendChild(container);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return container;
    }

    async function sendMessage() {
        const query = chatInput.value.trim();
        if (!query) return;
        const credentials = getCredentials();
        if (!credentials) return;

        appendMessage("user", query);
        chatInput.value = "";
        const loadingMsg = appendMessage("bot", "🧬 正在檢索並生成回答...");
        sendBtn.disabled = true;

        try {
            const response = await fetch(`${API_URL}/chat/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query, api_key: credentials.apiKey, password: credentials.password })
            });
            const data = await response.json();
            chatMessages.removeChild(loadingMsg);
            if (response.ok) appendMessage("bot", data.reply, data.sources);
            else {
                appendMessage("bot", `❌ 錯誤: ${data.detail || "內部伺服器錯誤"}`);
                if (response.status === 401) updateAuthUI('error');
            }
        } catch (error) {
            if (loadingMsg.parentNode) chatMessages.removeChild(loadingMsg);
            appendMessage("bot", "❌ 連線出錯。請檢查 API Key 或網路。");
        } finally {
            sendBtn.disabled = false;
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });
});
