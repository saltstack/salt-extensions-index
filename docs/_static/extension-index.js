document.addEventListener("DOMContentLoaded", () => {
  const filter = document.getElementById("extension-filter");
  const table = document.querySelector("table.extension-index");
  const count = document.getElementById("extension-count");
  if (!filter || !table) return;

  const rows = Array.from(table.querySelectorAll("tbody tr"));
  const update = () => {
    const query = filter.value.trim().toLowerCase();
    let visible = 0;
    for (const row of rows) {
      const matches = row.textContent.toLowerCase().includes(query);
      row.hidden = !matches;
      if (matches) visible += 1;
    }
    if (count) count.textContent = `${visible} of ${rows.length} extensions`;
  };

  filter.addEventListener("input", update);
  update();
});
