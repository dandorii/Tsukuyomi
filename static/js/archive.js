
document.addEventListener("DOMContentLoaded", () => {
    const revealElements = document.querySelectorAll(".archive-reveal");

    // Keep everything visible if the browser lacks IntersectionObserver.
    if (!("IntersectionObserver" in window)) {
        revealElements.forEach((element) => {
            element.classList.add("is-visible");
        });

        return;
    }

    const observer = new IntersectionObserver(
        (entries, currentObserver) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    currentObserver.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.15,
        }
    );

    revealElements.forEach((element) => {
        observer.observe(element);
    });
});
