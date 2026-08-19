const url = process.env.HEALTH_CHECK_URL ?? "http://127.0.0.1:5173";

const response = await fetch(url);
if (!response.ok) {
  console.error(`Health check failed: ${response.status} ${response.statusText}`);
  process.exit(1);
}

const html = await response.text();
if (!html.includes("Anil Kumar Kakelli")) {
  console.error("Health check failed: expected profile page content");
  process.exit(1);
}

console.log(`Health check passed for ${url}`);
