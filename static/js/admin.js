document.addEventListener('DOMContentLoaded', () => {
  const cmdInput = document.querySelector(".command-bar input[name='command']");
  const logContainer = document.getElementById("logContainer");
  const section = document.getElementById("logSection");
  const toggleButton = document.getElementById("terminal-toggle");
  const isFullScreenKey = "terminalFullScreen";

  // Restore fullscreen state from sessionStorage
  if (sessionStorage.getItem(isFullScreenKey) === "true") {
    section.classList.add("fullscreen");
  }

  // Focus input on load & handle command submission
  if (cmdInput) {
    cmdInput.focus();
    cmdInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        // Clear fullscreen before submitting command
        // sessionStorage.setItem(isFullScreenKey, "false");
        cmdInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    cmdInput.closest('form').submit();
  }
});
        cmdInput.closest('form').submit();
      }
    });
  }

  // Auto-scroll logs to bottom on load
  if (logContainer) {
    logContainer.scrollTop = logContainer.scrollHeight;
  }

  // Sync countdown timer
  const syncEpoch = parseInt(document.getElementById("admin-page").dataset.nextSync);
  function updateTimer() {
    const now = Math.floor(Date.now() / 1000);
    const remaining = Math.max(syncEpoch - now, 0);
    const minutes = Math.floor(remaining / 60);
    const seconds = remaining % 60;
    document.getElementById('sync-timer').textContent = `${minutes}m ${seconds}s`;
  }
  setInterval(updateTimer, 1000);
  updateTimer();

  // Fullscreen toggle button
  toggleButton.addEventListener("click", () => {
    console.log("Toggling fullscreen mode");
    section.classList.toggle("fullscreen");
    const isFull = section.classList.contains("fullscreen");
    sessionStorage.setItem(isFullScreenKey, isFull ? "true" : "false");
  });
});

// Modal popup to display user info
function showUserInfo(user) {
  const parsedUser = JSON.parse(user);
  const modal = document.getElementById("user-info-modal");
  const tableBody = document.getElementById("user-info-table");
  const emailTitle = document.getElementById("modal-user-email");
  const downloadBtn = document.getElementById("download-logs-btn");

  emailTitle.textContent = parsedUser.email || "User Info";
  tableBody.innerHTML = "";

  for (const [key, value] of Object.entries(parsedUser)) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <th style="text-transform: capitalize;">${key.replace(/_/g, " ")}</th>
      <td>${value ?? "—"}</td>
    `;
    tableBody.appendChild(row);
  }

  downloadBtn.href = `/download_logs/${encodeURIComponent(parsedUser.email)}`;
  modal.style.display = "flex";
}

// Close modal function
function hideModal() {
  document.getElementById("user-info-modal").style.display = "none";
}
