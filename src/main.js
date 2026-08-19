const button = document.querySelector("#greet");
const greeting = document.querySelector("#greeting");

button?.addEventListener("click", () => {
  const now = new Date().toLocaleString();
  greeting.textContent = `Hello from the Cloud Agent environment at ${now}.`;
});
