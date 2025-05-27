// Tab switching functionality
document.addEventListener("DOMContentLoaded", function () {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");

      // Remove active class from all tabs and panels
      tabBtns.forEach((b) => b.classList.remove("active"));
      tabPanels.forEach((p) => p.classList.remove("active"));

      // Add active class to clicked tab and corresponding panel
      btn.classList.add("active");
      document.getElementById(targetTab + "-panel").classList.add("active");
    });
  });
});

// File upload handling
function handleFileSelect(event) {
  const file = event.target.files[0];
  const fileInfo = document.getElementById("file-info");
  const submitBtn = document.getElementById("file-submit");

  if (file) {
    fileInfo.style.display = "block";
    fileInfo.innerHTML = `
            <i class="fas fa-file"></i>
            <strong>Selected:</strong> ${file.name} (${formatFileSize(
      file.size
    )})
        `;
    submitBtn.disabled = false;
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

// Process YouTube URL
async function processYouTube() {
  const url = document.getElementById("youtube-url").value;

  if (!url) {
    alert("Please enter a YouTube URL");
    return;
  }

  if (!isValidYouTubeUrl(url)) {
    alert("Please enter a valid YouTube URL");
    return;
  }

  showResults();
  showLoading();

  try {
    // Replace with your actual API endpoint
    const response = await fetch("/api/fact-check/youtube", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: url }),
    });

    const result = await response.json();
    displayResults(result);
  } catch (error) {
    displayError("Error processing YouTube video: " + error.message);
  }
}

// Process text input
async function processText() {
  const text = document.getElementById("text-input").value.trim();

  if (!text) {
    alert("Please enter some text to fact-check");
    return;
  }

  showResults();
  showLoading();

  try {
    // Replace with your actual API endpoint
    const response = await fetch("/api/fact-check/text", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: text }),
    });

    const result = await response.json();
    displayResults(result);
  } catch (error) {
    displayError("Error processing text: " + error.message);
  }
}

// Process file upload
async function processFile() {
  const fileInput = document.getElementById("file-input");
  const file = fileInput.files[0];

  if (!file) {
    alert("Please select a file");
    return;
  }

  showResults();
  showLoading();

  const formData = new FormData();
  formData.append("file", file);

  try {
    // Replace with your actual API endpoint
    const response = await fetch("/api/fact-check/file", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    displayResults(result);
  } catch (error) {
    displayError("Error processing file: " + error.message);
  }
}

// Utility functions
function isValidYouTubeUrl(url) {
  const youtubeRegex = /^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
  return youtubeRegex.test(url);
}

function showResults() {
  document.getElementById("results-section").style.display = "block";
  document
    .getElementById("results-section")
    .scrollIntoView({ behavior: "smooth" });
}

function showLoading() {
  document.getElementById("loading").style.display = "block";
  document.getElementById("results-container").innerHTML = "";
}

function hideLoading() {
  document.getElementById("loading").style.display = "none";
}

function displayResults(results) {
  hideLoading();
  const container = document.getElementById("results-container");

  if (!results || !results.facts || results.facts.length === 0) {
    container.innerHTML = "<p>No fact-checking results found.</p>";
    return;
  }

  let html = "";
  results.facts.forEach((fact) => {
    const statusClass = getStatusClass(fact.status);
    const statusIcon = getStatusIcon(fact.status);

    html += `
            <div class="fact-item ${statusClass}">
                <div class="fact-header">
                    <i class="${statusIcon}"></i>
                    <strong>${fact.claim || "Claim"}</strong>
                </div>
                <p class="fact-explanation">${
                  fact.explanation || "No explanation provided."
                }</p>
                <div class="fact-sources">
                    <small><strong>Confidence:</strong> ${
                      fact.confidence || "N/A"
                    }%</small>
                    ${
                      fact.sources
                        ? `<br><small><strong>Sources:</strong> ${fact.sources.join(
                            ", "
                          )}</small>`
                        : ""
                    }
                </div>
            </div>
        `;
  });

  container.innerHTML = html;
}

function displayError(message) {
  hideLoading();
  const container = document.getElementById("results-container");
  container.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
}

function getStatusClass(status) {
  switch (status?.toLowerCase()) {
    case "true":
    case "verified":
    case "correct":
      return "verified";
    case "false":
    case "incorrect":
    case "misleading":
      return "false";
    default:
      return "unclear";
  }
}

function getStatusIcon(status) {
  switch (status?.toLowerCase()) {
    case "true":
    case "verified":
    case "correct":
      return "fas fa-check-circle";
    case "false":
    case "incorrect":
    case "misleading":
      return "fas fa-times-circle";
    default:
      return "fas fa-question-circle";
  }
}
