const mobileMenuButton = document.querySelector(".mobile-menu-button");
const mobileMenu = document.querySelector("#mobile-menu");

if (mobileMenuButton && mobileMenu) {
  mobileMenuButton.addEventListener("click", () => {
    const open = mobileMenu.classList.toggle("open");
    mobileMenuButton.setAttribute("aria-expanded", String(open));
    mobileMenuButton.textContent = open ? "Close" : "Menu";
  });
}
