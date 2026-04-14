const API_URL = "/api/v1";

document.addEventListener("DOMContentLoaded", () => {
    // Elements
    const apiKeyInput = document.getElementById("api-key");
    const saveKeyBtn = document.getElementById("save-key-btn");
    const fileUpload = document.getElementById("file-upload");
    const uploadBtn = document.getElementById("upload-btn");
    const uploadStatus = document.getElementById("upload-status");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const chatMessages = document.getElementById("chat-messages");

    const demoPasswordInput = document.getElementById("demo-password");
    
    // Retrieve saved key from localStorage
    const savedKey = localStorage.getItem("google_api_key");
    if (savedKey) {
        apiKeyInput.value = savedKey;
        saveKeyBtn.textContent = "Saved";
        saveKeyBtn.classList.add("saved");
    }

    // Save key
    saveKeyBtn.addEventListener("click", () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            localStorage.setItem("google_api_key", key);
            saveKeyBtn.textContent = "Saved";
            setTimeout(() => { saveKeyBtn.textContent = "Save Key"; }, 2000);
        }
    });

    // Helper to get credentials
    const getCredentials = () => {
        const apiKey = apiKeyInput.value.trim() || localStorage.getItem("google_api_key") || "";
        const password = demoPasswordInput.value.trim() || "";
        
        if (!apiKey && !password) {
            alert("請輸入 Google API Key 或 Demo 存取密碼。");
            return null;
        }
        return { apiKey, password };
    };

    // Append Message to Chat
    const appendMessage = (sender, text, isSystem = false) => {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message");
        if (isSystem) {
            msgDiv.classList.add("system-message");
        } else {
            msgDiv.classList.add(sender === "user" ? "user-message" : "bot-message");
        }

        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv;
    };

    // Upload Document
    uploadBtn.addEventListener("click", async () => {
        const file = fileUpload.files[0];
        if (!file) {
            uploadStatus.textContent = "Please select a file.";
            uploadStatus.style.color = "var(--error)";
            return;
        }
        const credentials = getCredentials();
        if (!credentials) return;

        uploadStatus.textContent = "Uploading and processing...";
        uploadStatus.style.color = "var(--text-main)";
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
            const data = await response.json();

            if (response.ok) {
                uploadStatus.textContent = `Success! ${data.chunks_count} chunks processed.`;
                uploadStatus.style.color = "var(--success)";
                appendMessage("system", "Document trained successfully. You can now ask questions.", true);
            } else {
                throw new Error(data.detail || "Upload failed");
            }
        } catch (error) {
            uploadStatus.textContent = `Error: ${error.message}`;
            uploadStatus.style.color = "var(--error)";
        } finally {
            uploadBtn.disabled = false;
        }
    });

    // Send Chat Message
    const sendMessage = async () => {
        const query = chatInput.value.trim();
        if (!query) return;

        const credentials = getCredentials();
        if (!credentials) return;

        // Display user query
        appendMessage("user", query);
        chatInput.value = "";

        // Show loading
        const loadingMsg = appendMessage("bot", "Thinking...");
        sendBtn.disabled = true;

        try {
            const response = await fetch(`${API_URL}/chat/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ 
                    query, 
                    api_key: credentials.apiKey, 
                    password: credentials.password 
                })
            });

            const data = await response.json();

            // Remove loading
            chatMessages.removeChild(loadingMsg);

            if (response.ok) {
                const replyDiv = appendMessage("bot", data.reply);

                // If there are sources, append them
                if (data.sources && data.sources.length > 0) {
                    const sourceBox = document.createElement("div");
                    sourceBox.classList.add("source-box");
                    sourceBox.innerHTML = `<strong>Sources:</strong><ul>` +
                        data.sources.slice(0, 2).map(s => `<li>${s.metadata.source || 'Document'}</li>`).join('') +
                        `</ul>`;
                    replyDiv.appendChild(sourceBox);
                }
            } else {
                throw new Error(data.detail || "Chat request failed");
            }
        } catch (error) {
            if (chatMessages.contains(loadingMsg)) {
                chatMessages.removeChild(loadingMsg);
            }
            appendMessage("bot", `Error: ${error.message}`);
        } finally {
            sendBtn.disabled = false;
        }
    };

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});
