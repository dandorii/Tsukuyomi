document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("library-search-input");
    const searchStatus = document.getElementById("library-search-status");
    const clearButton = document.getElementById("library-search-clear");
    const letterCards = document.querySelectorAll(".library-card-link");

    if (!searchInput || !searchStatus) {
        return;
    }

    const cards = Array.from(letterCards);

    function filterLetters() {
        const query = searchInput.value.trim().toLowerCase();
        let visibleCount = 0;

        cards.forEach((card) => {
            const title = card.querySelector("h3")?.textContent || "";
            const preview = card.querySelector(".library-card-body")?.textContent || "";
            const searchableText = `${title} ${preview}`.toLowerCase();

            const matches = searchableText.includes(query);

            card.hidden = !matches;

            if (matches) {
                visibleCount++;
            }
        });

        if (query === "") {
            searchStatus.textContent = "";
        } else if (visibleCount === 0) {
            searchStatus.textContent = "No letters found. Try another search.";
        } else {
            searchStatus.textContent =
                `${visibleCount} ${visibleCount === 1 ? "letter" : "letters"} found.`;
        }
    }

    searchInput.addEventListener("input", filterLetters);
        if (clearButton) {
            clearButton.addEventListener("click", () => {
                searchInput.value = "";
                filterLetters();
                searchInput.focus();
            });
        }
});