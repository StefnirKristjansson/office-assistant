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
          responseType: "blob", // Important for handling binary data
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${tokenInput.value}`,
          },
        }
      );

      // Create a blob from the response data
      const blob = new Blob([response.data], {
        type: response.headers["content-type"],
      });

      // Create a link to download the file
      const downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      // Use the filename from the response headers if available
      const contentDisposition = response.headers["content-disposition"];
      let filename = "Frodi_minnisblad.docx";
      if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
        if (fileNameMatch.length === 2) filename = fileNameMatch[1];
      }
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(downloadUrl);

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
