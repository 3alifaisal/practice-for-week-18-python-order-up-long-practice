// Function to auto-dismiss flash messages
document.addEventListener("DOMContentLoaded", () => {
  const flashMessages = document.querySelectorAll(".flash-messages");
  flashMessages.forEach((message) => {
    setTimeout(() => {
      message.style.opacity = "0"; // Fade out
      setTimeout(() => {
        message.remove(); // Remove from DOM after fade-out
      }, 500); // Delay for fade-out transition
    }, 1500); // Visible for 3 seconds
  });
});
