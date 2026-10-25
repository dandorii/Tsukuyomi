
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

/* REFLECTION TYPEWRITER WITH SKIP SUPPORT */
document.addEventListener("DOMContentLoaded", () => {
    const eyebrow = document.querySelector(".reflection-eyebrow");
    const title = document.querySelector(".typewriter-title");
    const date = document.querySelector(".reflection-date");
    const paragraphs = document.querySelectorAll(".reflection-body p");

    const skipButton = document.querySelector(".skip-typewriter");
    const invitation = document.querySelector(".reflection-invitation");
    const farewell = document.querySelector(".reflection-farewell");
    const returnLink = document.querySelector(".reflection-return");

    if (!title) return;

    const textElements = [
        eyebrow,
        title,
        date,
        ...paragraphs,
    ].filter(Boolean);

    // Save the original text before the typewriter clears it.
    const originalTexts = new Map(
        textElements.map((element) => [
            element,
            element.textContent.trim(),
        ])
    );

    let skipRequested = false;
    let activeTimer = null;
    let resolveCurrentTyping = null;

    const revealEnding = () => {
        [invitation, farewell, returnLink].forEach((element) => {
            if (element) {
                element.classList.add("is-visible");
            }
        });
    };

    const finishImmediately = () => {
        skipRequested = true;

        if (activeTimer !== null) {
            clearTimeout(activeTimer);
            activeTimer = null;
        }

        // Reveal every piece of text in its original form.
        textElements.forEach((element) => {
            element.textContent = originalTexts.get(element);
            element.classList.remove("is-typing");
            element.classList.add("is-typed");
        });

        revealEnding();

        if (skipButton) {
            skipButton.hidden = true;
        }

        // Release the currently waiting typewriter promise.
        if (resolveCurrentTyping) {
            const resolve = resolveCurrentTyping;
            resolveCurrentTyping = null;
            resolve();
        }
    };

    const typeText = (element, text, speed) => {
        return new Promise((resolve) => {
            let index = 0;
            resolveCurrentTyping = resolve;

            element.textContent = "";
            element.classList.add("is-typing");

            function typeNextCharacter() {
                if (skipRequested) {
                    resolveCurrentTyping = null;
                    resolve();
                    return;
                }

                if (index < text.length) {
                    element.textContent += text.charAt(index);
                    index++;

                    activeTimer = setTimeout(
                        typeNextCharacter,
                        speed
                    );
                } else {
                    activeTimer = null;
                    element.classList.remove("is-typing");
                    element.classList.add("is-typed");

                    resolveCurrentTyping = null;
                    resolve();
                }
            }

            typeNextCharacter();
        });
    };

    const pause = (duration) =>
        new Promise((resolve) => {
            activeTimer = setTimeout(() => {
                activeTimer = null;
                resolve();
            }, duration);
        });

    async function startTyping() {
        textElements.forEach((element) => {
            element.classList.remove("is-typing", "is-typed");
        });

        if (skipButton) {
            skipButton.hidden = false;
        }

        if (eyebrow) {
            await typeText(
                eyebrow,
                originalTexts.get(eyebrow),
                70
            );

            if (skipRequested) return;
            await pause(250);
            if (skipRequested) return;
        }

        await typeText(title, originalTexts.get(title), 100);
        if (skipRequested) return;

        if (date) {
            await pause(250);
            if (skipRequested) return;

            await typeText(date, originalTexts.get(date), 70);
            if (skipRequested) return;
        }

        for (const paragraph of paragraphs) {
            await pause(350);
            if (skipRequested) return;

            await typeText(
                paragraph,
                originalTexts.get(paragraph),
                25
            );

            if (skipRequested) return;
        }

        await pause(1200);
        if (skipRequested) return;

        if (invitation) {
            invitation.classList.add("is-visible");
        }

        await pause(900);
        if (skipRequested) return;

        if (farewell) {
            farewell.classList.add("is-visible");
        }

        await pause(900);
        if (skipRequested) return;

        if (returnLink) {
            returnLink.classList.add("is-visible");
        }

        if (skipButton) {
            skipButton.hidden = true;
        }
    }

    if (skipButton) {
        skipButton.addEventListener("click", finishImmediately);
    }

    startTyping();
});

/* MOONLIT READING PROGRESS */
document.addEventListener("DOMContentLoaded", () => {
    const progressBar = document.querySelector(".reading-progress-bar");

    if (!progressBar) return;

    function updateReadingProgress() {
        const scrollableHeight =
            document.documentElement.scrollHeight - window.innerHeight;

        if (scrollableHeight <= 0) {
            progressBar.style.width = "0%";
            return;
        }

        const progress =
            (window.scrollY / scrollableHeight) * 100;

        progressBar.style.width = `${Math.min(progress, 100)}%`;
    }

    window.addEventListener("scroll", updateReadingProgress, {
        passive: true,
    });

    window.addEventListener("resize", updateReadingProgress);

    updateReadingProgress();
});

