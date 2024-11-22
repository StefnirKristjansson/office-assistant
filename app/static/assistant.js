// chat.js

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
        // Display assistant's response
        const assistantMessage = data.content; // Adjust based on your backend response structure

        const assistantMessageDiv = document.createElement("div");
        assistantMessageDiv.classList.add("mb-4");
        assistantMessageDiv.innerHTML = `
          <div class="bg-gray-200 p-4 rounded-lg max-w-md">
            <p class="text-gray-800">${assistantMessage}</p>
          </div>
        `;
        chatContainer.appendChild(assistantMessageDiv);

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
