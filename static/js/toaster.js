function toastfunc(color, message) {
  let snackbar = document.getElementById("snackbar");
  if (!snackbar) {
    snackbar = document.createElement("div");
    console.log('toastfunc called with:', color, message);
    snackbar.id = "snackbar";
    snackbar.style = `
      visibility: hidden;
      min-width: 250px;
      background-color: ${color || "#333"};
      color: #fff;
      text-align: center;
      border-radius: 5px;
      padding: 16px;
      position: fixed;
      z-index: 9999; /* Ensure it’s above other elements */
      left: 50%;
      transform: translateX(-50%);
      top: 30px;
      font-size: 16px;
      box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    `;
    document.body.appendChild(snackbar);
  }

  snackbar.style.backgroundColor = color || "#333";
  snackbar.textContent = message || "Default message";
  snackbar.style.visibility = "visible";

  setTimeout(() => {
    snackbar.style.visibility = "hidden";
  }, 3000);
}
