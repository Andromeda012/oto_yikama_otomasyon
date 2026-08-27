(function () {
  const menuBtn = document.getElementById("menuBtn");
  const backdrop = document.getElementById("sidebarBackdrop");

  function closeNav() {
    document.body.classList.remove("nav-open");
    if (backdrop) backdrop.hidden = true;
  }

  function openNav() {
    document.body.classList.add("nav-open");
    if (backdrop) backdrop.hidden = false;
  }

  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      if (document.body.classList.contains("nav-open")) {
        closeNav();
      } else {
        openNav();
      }
    });
  }

  if (backdrop) {
    backdrop.addEventListener("click", closeNav);
  }

  document.querySelectorAll(".nav-toggle").forEach(function (button) {
    button.addEventListener("click", function () {
      const group = button.parentElement;
      const willOpen = !group.classList.contains("is-open");
      group.classList.toggle("is-open", willOpen);
      button.setAttribute("aria-expanded", willOpen ? "true" : "false");
    });
  });
})();
