const draftList = document.getElementById("draft-list");
const draftListStatus = document.getElementById("draft-list-status");
const pageContent = document.querySelector(".archive-page");

const deleteLetterModal = document.getElementById("delete-letter-modal");
const cancelDeleteButton = document.getElementById("cancel-delete-letter");
const confirmDeleteButton = document.getElementById("confirm-delete-letter");

function formatDraftDate(timestamp) {
    if (!timestamp) {
        return "Unknown date";
    }

    // SQLite timestamps use UTC, so interpret them as UTC.
    const normalizedTimestamp = timestamp.includes("T")
        ? timestamp
        : `${timestamp.replace(" ", "T")}Z`;

    const date = new Date(normalizedTimestamp);

    if (Number.isNaN(date.getTime())) {
        return timestamp;
    }

    return new Intl.DateTimeFormat(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        hourCycle: "h23"
    }).format(date);
}

async function loadDrafts() {
    draftListStatus.textContent = "Looking for your letters beneath the moon...";
    draftList.replaceChildren();

    try {
        const response = await fetch("/api/drafts");

        if (!response.ok) {
            throw new Error("Unable to retrieve your saved letters.");
        }

        const data = await response.json();

        if (!Array.isArray(data.drafts)) {
            throw new Error("The server returned an unexpected response.");
        }

        if (data.drafts.length === 0) {
            draftListStatus.textContent = "YOUR COLLECTION IS QUIET.";

            const emptyState = document.createElement("section");
            emptyState.className = "draft-empty-state";

            const moon = document.createElement("p");
            moon.className = "draft-empty-moon";
            moon.setAttribute("aria-hidden", "true");
            moon.textContent = "☾";

            const heading = document.createElement("h3");
            heading.textContent = "NO LETTERS, FOR NOW.";

            const message = document.createElement("p");
            message.textContent =
                "Some words have not found their way onto the page yet. There is no rush. When you are ready, the writing room is waiting.";

            const writeLink = document.createElement("a");
            writeLink.className = "draft-open-link";
            writeLink.href = "/write";
            writeLink.textContent = "WRITE YOUR FIRST LETTER →";

            emptyState.append(moon, heading, message, writeLink);
            draftList.appendChild(emptyState);

            return;
        }

        draftListStatus.textContent =
            `${data.drafts.length} saved ${data.drafts.length === 1 ? "letter" : "letters"}`;

        data.drafts.forEach((draft) => {
            const card = document.createElement("article");
            card.className = "entry-placeholder draft-card";

            const category = document.createElement("p");
            category.className = "reflection-category";
            category.textContent = draft.sealed
                ? "SEALED — NOT SENT"
                : "UNSENT LETTER";

            const title = document.createElement("h3");
            title.textContent = draft.title || "UNTITLED LETTER";

            const recipient = document.createElement("p");
            recipient.className = "reflection-excerpt";
            recipient.textContent = draft.recipient
                ? `Written for: ${draft.recipient}`
                : "No recipient specified";

            const createdDate = document.createElement("p");
            createdDate.className = "reflection-date";
            createdDate.textContent =
                `FIRST WRITTEN: ${formatDraftDate(draft.created_at)}`;

            const updatedDate = document.createElement("p");
            updatedDate.className = "reflection-date";
            updatedDate.textContent =
                `LAST KEPT: ${formatDraftDate(draft.updated_at)}`;

            
            const openLink = document.createElement("a");
            openLink.className = "draft-open-link";
            openLink.href = `/my-letters/${encodeURIComponent(draft.id)}`;
            openLink.textContent = "READ LETTER →";

            let deleteButton = null;

            if (!draft.sealed) {
                deleteButton = document.createElement("button");
                deleteButton.type = "button";
                deleteButton.className = "draft-delete-button";
                deleteButton.textContent = "DELETE LETTER";

                deleteButton.addEventListener("click", () => {
                    openDeleteModal(draft, deleteButton);
                });
            }

            card.append(
                category,
                title,
                recipient,
                createdDate,
                updatedDate,
                openLink,
            );

            if (deleteButton) {
                card.appendChild(deleteButton);
            }
            
            draftList.appendChild(card);
        });
    } catch (error) {
        draftListStatus.textContent =
            error.message || "Something went wrong while finding your letters.";
    }
}

let draftPendingDeletion = null;
let deleteButtonPendingDeletion = null;

function openDeleteModal(draft, deleteButton) {
    draftPendingDeletion = draft;
    deleteButtonPendingDeletion = deleteButton;

    pageContent.inert = true;
    deleteLetterModal.hidden = false;
    cancelDeleteButton.focus();
}

function closeDeleteModal() {
    deleteLetterModal.hidden = true;
    pageContent.inert = false;

    draftPendingDeletion = null;
    deleteButtonPendingDeletion = null;
}

document.addEventListener("keydown", (event) => {
    if (deleteLetterModal.hidden) {
        return;
    }

    if (event.key === "Escape") {
        event.preventDefault();

        const previousButton = deleteButtonPendingDeletion;

        closeDeleteModal();
        previousButton?.focus();
        return;
    }

    if (event.key === "Tab") {
        const focusableElements = [
            cancelDeleteButton,
            confirmDeleteButton
        ].filter((element) => !element.disabled);

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey && document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
        } else if (
            !event.shiftKey &&
            document.activeElement === lastElement
        ) {
            event.preventDefault();
            firstElement.focus();
        }
    }
});

cancelDeleteButton.addEventListener("click", () => {
    const previousButton = deleteButtonPendingDeletion;

    closeDeleteModal();
    previousButton?.focus();
});

deleteLetterModal.addEventListener("click", (event) => {
    if (event.target === deleteLetterModal) {
        const previousButton = deleteButtonPendingDeletion;

        closeDeleteModal();
        previousButton?.focus();
    }
});

confirmDeleteButton.addEventListener("click", async () => {
    if (!draftPendingDeletion) {
        return;
    }

    const draft = draftPendingDeletion;

    confirmDeleteButton.disabled = true;
    confirmDeleteButton.textContent = "LETTING GO...";

    try {
        const response = await fetch(
            `/api/drafts/${encodeURIComponent(draft.id)}`,
            { method: "DELETE" }
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to delete this letter.");
        }

        closeDeleteModal();
        await loadDrafts();
    } catch (error) {
        window.alert(
            error.message || "Something went wrong while deleting this letter."
        );
    } finally {
        confirmDeleteButton.disabled = false;
        confirmDeleteButton.textContent = "LET IT GO";
    }
});

loadDrafts();