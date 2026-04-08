document.querySelectorAll(".nav-dropdown").forEach(group => {
    const btn = group.querySelector(".nav-toggle");
    btn.addEventListener("click", e => {
        e.preventDefault();
        const isShown = group.classList.contains("show");
        document.querySelectorAll(".nav-dropdown").forEach(item => item.classList.remove("show"));
        if (!isShown) {
            group.classList.add("show");
        }
    });
});

const avatarDropdown = document.getElementById("avatarDropdown");
const avatarBtn = document.getElementById("avatarBtn");
if (avatarDropdown && avatarBtn) {
    let closeTimer = null;
    const openMenu = () => {
        if (closeTimer) {
            clearTimeout(closeTimer);
            closeTimer = null;
        }
        avatarDropdown.classList.add("show");
    };
    const closeMenuDelay = () => {
        closeTimer = setTimeout(() => {
            avatarDropdown.classList.remove("show");
        }, 250);
    };
    avatarBtn.addEventListener("click", e => {
        e.preventDefault();
        avatarDropdown.classList.toggle("show");
    });
    avatarDropdown.addEventListener("mouseenter", openMenu);
    avatarDropdown.addEventListener("mouseleave", closeMenuDelay);
    document.addEventListener("click", e => {
        if (!avatarDropdown.contains(e.target)) {
            avatarDropdown.classList.remove("show");
        }
    });
}
