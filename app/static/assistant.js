document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");
  const chatContainer = document.getElementById("chat-container");

  const randomResponses = [
    "I'm sorry, could you please clarify?",
    "That's interesting!",
    "Could you tell me more?",
    "I'm here to help!",
    "Let me think about that.",
    "Absolutely!",
    "I'm not sure I understand.",
    "Can you provide an example?",
    "Sure, let's discuss that.",
    "Thank you for sharing that.",
  ];

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

    // Simulate assistant response
    setTimeout(() => {
      const randomIndex = Math.floor(Math.random() * randomResponses.length);
      const assistantMessage = randomResponses[randomIndex];

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
    }, 1000); // Simulate response delay
  });
});
