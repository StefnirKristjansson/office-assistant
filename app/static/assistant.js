document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");
  const chatContainer = document.getElementById("chat-container");
  const typingIndicator = document.createElement("div");
  typingIndicator.id = "typing-indicator";
  typingIndicator.classList.add("mb-4", "text-gray-500");
  typingIndicator.textContent = "Assistant is typing...";
  let threadId = localStorage.getItem("thread_id");

  // Clear thread ID on page refresh
  window.addEventListener("load", () => {
    localStorage.removeItem("thread_id");
    document.cookie = "thread_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  });

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

    // Show typing indicator
    chatContainer.appendChild(typingIndicator);

    // Send the user's message to the backend
    fetch("/adstod/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userMessage, thread_id: threadId }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Store thread ID in local storage
        if (!threadId) {
          threadId = data.thread_id;
          localStorage.setItem("thread_id", threadId);
        }

        // Display the new message
        const assistantMessageDiv = document.createElement("div");
        assistantMessageDiv.classList.add("mb-4", "flex", "justify-start");
        assistantMessageDiv.innerHTML = `
          <div class="bg-gray-200 text-gray-800 p-4 rounded-lg max-w-md">
            <p>${data.message}</p>
          </div>
        `;
        chatContainer.appendChild(assistantMessageDiv);

        // Scroll to the bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Hide typing indicator
        typingIndicator.remove();
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

        // Hide typing indicator
        typingIndicator.remove();
      });
  });
});
