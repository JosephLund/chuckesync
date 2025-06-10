document.addEventListener('DOMContentLoaded', () => {
  const cmdInput = document.querySelector(".command-bar input[name='command']");
  const logContainer = document.querySelector(".log-container");

  if (cmdInput) {
    cmdInput.focus();
    cmdInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        cmdInput.closest('form').submit();
      }
    });
  }

  if (logContainer) {
    logContainer.scrollTop = logContainer.scrollHeight;
  }

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
});


function showUserInfo(user) {
  const modal = document.getElementById("user-info-modal");
  const tableBody = document.getElementById("user-info-table");
  const emailTitle = document.getElementById("modal-user-email");
  const downloadBtn = document.getElementById("download-logs-btn");

  emailTitle.textContent = user.email || "User Info";
  tableBody.innerHTML = "";

  for (const [key, value] of Object.entries(user)) {
    const row = document.createElement("tr");

    row.innerHTML = `
      <th style="text-transform: capitalize;">${key.replace(/_/g, " ")}</th>
      <td>${value ?? "—"}</td>
    `;

    tableBody.appendChild(row);
  }

  // Update download URL with email
  downloadBtn.href = `/download_logs/${encodeURIComponent(user.email)}`;

  modal.style.display = "flex";
}

function hideModal() {
  document.getElementById("user-info-modal").style.display = "none";
}