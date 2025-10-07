function maskSite() {
  let wrap = document.createElement('div');
  wrap.style.display = 'none';
  let el = document.getElementById("siteName");
  wrap.replaceChildren(...el.children);
  el.replaceChildren(wrap);
  let label = document.createElement("div");
  label.textContent = el.dataset.name + (el.dataset.crew ? " (" + el.dataset.crew + ") " : "")
  let button = document.createElement("button");
  button.textContent = el.dataset.name ? "Change Site" : "Set Site";
  button.style.marginLeft = "1rem";
  label.append(button)
  el.append(label)

  button.onclick = (ev) => {
    ev.preventDefault();
    wrap.style.display = "block";
    button.style.display = "none";
    label.style.display = "none";
  }
}


document.addEventListener("DOMContentLoaded", (event) => {
  maskSite();
});
