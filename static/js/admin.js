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