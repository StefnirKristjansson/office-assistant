document
  .getElementById("upload-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent the default form submission

    const fileInput = document.getElementById("file");
    const tokenInput = document.getElementById("token");

    if (fileInput.files.length === 0) {
      alert("Please select a file to upload.");
      return;
    }

    if (!tokenInput.value) {
      alert("Please enter your token.");
      return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    // Get selected chapters
    const selectedChapters = [];
    document
      .querySelectorAll('input[name="chapters"]:checked')
      .forEach((checkbox) => {
        selectedChapters.push(checkbox.value);
      });
    formData.append("chapters", JSON.stringify(selectedChapters));

    // Disable the button and show the loading icon and message
    const uploadButton = document.querySelector('button[type="submit"]');
    uploadButton.disabled = true;
    document.getElementById("loading").classList.remove("hidden");

    try {
      const response = await axios.post(
        "/minnisblad-adstod/upload/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${tokenInput.value}`,
          },
        }
      );

      // Process the JSON response
      const jsonResponse = response.data;

      // Extract and format text content for display
      const malfarText = jsonResponse.properties.malfar
        .replace(/\\n/g, "<br>")
        .replace(/\\"/g, '"');
      const radleggingarText = jsonResponse.properties.radleggingar
        .replace(/\\n/g, "<br>")
        .replace(/\\"/g, '"');

      // Populate the input fields with the JSON data
      document.getElementById("malfar").value = jsonResponse.malfar;
      document.getElementById("stafsetning").value = jsonResponse.stafsetning;
      document.getElementById("radleggingar").value = jsonResponse.radleggingar;

      // Display the formatted JSON response in the containers
      document.getElementById("malfar-text").innerHTML = malfarText;
      document.getElementById("malfar-message").classList.remove("hidden");
      document.getElementById("radleggingar-text").innerHTML = radleggingarText;
      document
        .getElementById("radleggingar-message")
        .classList.remove("hidden");

      // Display the success message
      document.getElementById("success-message").classList.remove("hidden");

      // Clear the file input and token input
      fileInput.value = "";
      tokenInput.value = "";
    } catch (error) {
      console.error(error);
      document.getElementById("error-message").classList.remove("hidden");
      if (error.response && error.response.data) {
        const reader = new FileReader();
        reader.onload = function () {
          document.getElementById("error-text").innerText = reader.result;
        };
        reader.readAsText(error.response.data);
      } else {
        document.getElementById("error-text").innerText =
          "An unexpected error occurred.";
      }
    } finally {
      // Re-enable the button and hide the loading icon and message
      uploadButton.disabled = false;
      document.getElementById("loading").classList.add("hidden");
    }
  });
