document.getElementById("userMessage").addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevents newline in input field
            sendMessage();
        }
    });


    function toggleChatbot() {
        let chatbot = document.getElementById("chatbotContainer");
        chatbot.classList.toggle("active"); // Toggle visibility
    }

    function sendMessage() {
    let message = document.getElementById("userMessage").value;
    if (!message.trim()) return; // Prevent empty messages

    let chatBox = document.getElementById("chatBox");

    // Append user message
    let userMessageHTML = `<div class="item right"><div class="msg">${message}</div></div>`;
    chatBox.innerHTML += userMessageHTML;
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send message to backend
    fetch("/chatbot/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        // Append bot response with "bot" class
        let botMessageHTML = `<div class="item"><div class="msg bot">${data.response}</div></div>`;
        chatBox.innerHTML += botMessageHTML;
        chatBox.scrollTop = chatBox.scrollHeight;
        document.getElementById("userMessage").value = "";
    })
    .catch(error => {
        console.error("Error:", error);
    });
    }