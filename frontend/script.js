document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "/api/v1"; // Using relative path for deployment
    
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
    
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const chatMessages = document.getElementById("chat-messages");

    // UI Feedback Logic
    function updateAuthUI(state) {
        // state: 'locked' (amber), 'success' (green), 'error' (red)
        authStatus.className = "status-indicator"; // reset
        
        if (state === 'success') {
            authStatus.classList.add("unlocked");
            saveKeyBtn.textContent = "Vault Secured";
            saveKeyBtn.style.background = "var(--success)";
            if(verifyDemoBtn) verifyDemoBtn.textContent = "Verified";
        } else if (state === 'error') {
            authStatus.style.background = "var(--error)";
            authStatus.style.boxShadow = "0 0 12px var(--error)";
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

    // Verify Credentials with Backend
    async function verifyCredentials(apiKey = "", password = "") {
        updateAuthUI('loading');
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
        // Basic check for UI, but don't call backend to avoid token usage on load
        updateAuthUI('success');
    }

    // Event Listeners
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
        if (password) {
            verifyCredentials("", password);
        }
    });

    // Helper to get credentials for actual requests
    const getCredentials = () => {
        const apiKey = apiKeyInput.value.trim() || localStorage.getItem("google_api_key") || "";
        const password = demoPasswordInput.value.trim() || "";
        
        if (!apiKey && !password) {
            alert("🔒 請解鎖金庫：請點擊或是輸入憑證解鎖。");
            return null;
        }
        return { apiKey, password };
    };

    // File Upload Handling
    dropzone.addEventListener("click", () => fileUpload.click());
    fileUpload.addEventListener("change", (e) => {
        if (e.target.files.length > 0) fileNameDisplay.textContent = e.target.files[0].name;
    });

    uploadBtn.addEventListener("click", async () => {
        const file = fileUpload.files[0];
        if (!file) {
            uploadStatus.textContent = "❌ 請先選擇檔案";
            uploadStatus.style.color = "var(--error)";
            return;
        }
        
        const credentials = getCredentials();
        if (!credentials) return;

        uploadStatus.textContent = "⏳ 正在將知識注入庫中...";
        uploadStatus.style.color = "var(--primary)";
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
                uploadStatus.style.color = "var(--success)";
            } else {
                const error = await response.json();
                uploadStatus.textContent = `❌ 失敗: ${error.detail || "驗證失敗"}`;
                uploadStatus.style.color = "var(--error)";
                if (response.status === 401) updateAuthUI('error');
            }
        } catch (error) {
            uploadStatus.textContent = "❌ 連線錯誤";
            uploadStatus.style.color = "var(--error)";
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
            sourcesHtml = `
                <div class="source-box">
                    <strong>📚 來源引用:</strong><br>
                    ${sources.map(s => `• 第 ${s.page} 頁: ${s.content.substring(0, 80)}...`).join("<br>")}
                </div>`;
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
        const loadingMsg = appendMessage("bot", "🧬 正在檢索知識庫並生成回答...");
        sendBtn.disabled = true;

        try {
            const response = await fetch(`${API_URL}/chat/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query, api_key: credentials.apiKey, password: credentials.password })
            });

            const data = await response.json();
            chatMessages.removeChild(loadingMsg);

            if (response.ok) {
                appendMessage("bot", data.reply, data.sources);
            } else {
                appendMessage("bot", `❌ 發生錯誤: ${data.detail || "無法連線"}`);
                if (response.status === 401) updateAuthUI('error');
            }
        } catch (error) {
            if (loadingMsg.parentNode) chatMessages.removeChild(loadingMsg);
            appendMessage("bot", "❌ 網路連線出錯。");
        } finally {
            sendBtn.disabled = false;
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });
});
