document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");
  const chatContainer = document.getElementById("chat-container");

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const userMessage = messageInput.value.trim();
    if (userMessage === "") return;

    // Display user message
    const userMessageDiv = document.createElement("div");
    userMessageDiv.classList.add("mb-4", "flex", "justify-end");
    userMessageDiv.innerHTML = `
      <div class="bg-blue-500 text-white p-4 rounded-lg max-w-md">
        <p>${userMessage}</p>
      </div>
    `;
    chatContainer.appendChild(userMessageDiv);
    messageInput.value = "";

    // Scroll to the bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Send the user's message to the backend
    fetch("/adstod/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userMessage }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Display the entire chat history
        chatContainer.innerHTML = "";
        data.history.forEach((msg) => {
          const messageDiv = document.createElement("div");
          messageDiv.classList.add("mb-4", msg.role === "user" ? "flex" : "justify-end");
          messageDiv.innerHTML = `
            <div class="${msg.role === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-800"} p-4 rounded-lg max-w-md">
              <p>${msg.content}</p>
            </div>
          `;
          chatContainer.appendChild(messageDiv);
        });

        // Scroll to the bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
      })
      .catch((error) => {
        console.error("Error:", error);
        // Optionally display an error message in the chat
        const errorMessageDiv = document.createElement("div");
        errorMessageDiv.classList.add("mb-4");
        errorMessageDiv.innerHTML = `
          <div class="bg-red-200 p-4 rounded-lg max-w-md">
            <p class="text-red-800">An error occurred. Please try again.</p>
          </div>
        `;
        chatContainer.appendChild(errorMessageDiv);
      });
  });
});
