document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");
  const chatContainer = document.getElementById("chat-container");
  // When the page loads clear the localStorage
  localStorage.clear();

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const userMessage = messageInput.value.trim();
    if (userMessage === "") return;

    let thread_id = localStorage.getItem("thread_id");
    console.log("Thread ID from localStorage:", thread_id);
    if (thread_id === null) {
      thread_id = "";
    }
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
      body: JSON.stringify({ message: userMessage, thread_id: thread_id }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Display assistant response
        const assistantMessageDiv = document.createElement("div");
        assistantMessageDiv.classList.add("mb-4");
        assistantMessageDiv.innerHTML = `
          <div class="bg-gray-200 p-4 rounded-lg max-w-md">
            <p>${data.message}</p>
          </div>
        `;
        chatContainer.appendChild(assistantMessageDiv);

        // Store the thread ID in localStorage
        if (data.thread_id) {
          localStorage.setItem("thread_id", data.thread_id);
          console.log("Thread ID stored in localStorage as:", data.thread_id);
        } else {
          console.log("No thread ID received from the backend");
        }

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
