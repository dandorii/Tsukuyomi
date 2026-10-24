
const letterBody = document.getElementById("letter-body");
const characterCount = document.getElementById("letter-character-count");

const clearLetterButton = document.getElementById("clear-letter");
const letterTitle = document.getElementById("letter-title");
const letterRecipient = document.getElementById("letter-recipient");

const letterModal = document.getElementById("letter-modal");
const cancelClearLetter = document.getElementById("cancel-clear-letter");
const confirmClearLetter = document.getElementById("confirm-clear-letter");

const saveDraftButton = document.getElementById("save-draft");
const draftSavedModal = document.getElementById("draft-saved-modal");
const draftSavedTitle = document.getElementById("draft-saved-title");
const draftSavedMessage = document.getElementById("draft-saved-message");
const closeDraftSavedButton = document.getElementById("close-draft-saved");
const currentUrl = new URL(window.location.href);
const draftId = currentUrl.searchParams.get("id");

let currentDraftId = null;

async function loadExistingDraft() {
    if (!draftId) {
        return;
    }

    if (!/^\d+$/.test(draftId)) {
        alert("That letter link is invalid.");
        return;
    }

    try {
        const response = await fetch(
            `/api/drafts/${encodeURIComponent(draftId)}`
        );

        const result = await response.json();

        if (!response.ok) {
            saveDraftButton.disabled = true;

            throw new Error(
                result.error || "Unable to open this letter."
            );
        }

        const draft = result.draft;

        letterTitle.value = draft.title || "";
        letterRecipient.value = draft.recipient || "";
        letterBody.value = draft.body || "";

        currentDraftId = draft.id;

        letterBody.dispatchEvent(
            new Event("input", { bubbles: true })
        );
    } catch (error) {
        saveDraftButton.disabled = true;
        alert(error.message || "Unable to open this letter.");
    }
}

loadExistingDraft();

// Character counter
if (letterBody && characterCount) {
    function updateCharacterCount() {
        const count = letterBody.value.length;

        characterCount.textContent =
            `${count} ${count === 1 ? "character" : "characters"}`;
    }

    letterBody.addEventListener("input", updateCharacterCount);
    updateCharacterCount();
}

// Clear Letter confirmation modal
if (
    clearLetterButton &&
    letterTitle &&
    letterRecipient &&
    letterBody &&
    letterModal &&
    cancelClearLetter &&
    confirmClearLetter
) {
    function openClearModal() {
        letterModal.hidden = false;
        document.body.style.overflow = "hidden";
        cancelClearLetter.focus();
    }

    function closeClearModal() {
        letterModal.hidden = true;
        document.body.style.overflow = "";
        clearLetterButton.focus();
    }

    clearLetterButton.addEventListener("click", openClearModal);

    cancelClearLetter.addEventListener("click", closeClearModal);

    confirmClearLetter.addEventListener("click", function () {
        letterTitle.value = "";
        letterRecipient.value = "";
        letterBody.value = "";

        letterBody.dispatchEvent(new Event("input", { bubbles: true }));

        closeClearModal();
    });

    letterModal.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            event.preventDefault();
            closeClearModal();
            return;
        }

        if (event.key === "Tab") {
            if (
                event.shiftKey &&
                document.activeElement === cancelClearLetter
            ) {
                event.preventDefault();
                confirmClearLetter.focus();
            } else if (
                !event.shiftKey &&
                document.activeElement === confirmClearLetter
            ) {
                event.preventDefault();
                cancelClearLetter.focus();
            }
        }
    });

    letterModal.addEventListener("focusout", function () {
        if (letterModal.hidden) {
            return;
        }

        requestAnimationFrame(function () {
            if (!letterModal.contains(document.activeElement)) {
                cancelClearLetter.focus();
            }
        });
    });
}

// Save Draft confirmation popup
if (
    saveDraftButton &&
    draftSavedModal &&
    draftSavedTitle &&
    draftSavedMessage &&
    closeDraftSavedButton &&
    letterTitle &&
    letterRecipient &&
    letterBody
) {
    function openDraftSavedModal(title, message) {
        draftSavedTitle.textContent = title;
        draftSavedMessage.textContent = message;

        draftSavedModal.hidden = false;
        document.body.style.overflow = "hidden";

        closeDraftSavedButton.focus();
    }

    function closeDraftSavedModal() {
        draftSavedModal.hidden = true;
        document.body.style.overflow = "";
        saveDraftButton.focus();
    }

    saveDraftButton.addEventListener("click", async function () {
        saveDraftButton.disabled = true;

        try {
             const isEditingExistingDraft = currentDraftId !== null;
                const response = await fetch(
                    isEditingExistingDraft
                        ? `/api/drafts/${currentDraftId}`
                        : "/api/drafts",
                    {
                        method: isEditingExistingDraft ? "PUT" : "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            title: letterTitle.value,
                            recipient: letterRecipient.value,
                            body: letterBody.value
                        })
                    }
                );

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.error || "Unable to save your draft."
                );
            }

            if (!isEditingExistingDraft) {
                currentDraftId = result.id;
            }
            
            openDraftSavedModal(
                "YOUR WORDS ARE SAFE.",
                isEditingExistingDraft
                    ? "LETTER UPDATED — STILL UNSENT."
                    : "DRAFT SAVED — NOT SENT."
            );
        } catch (error) {
            openDraftSavedModal(
                "DRAFT NOT SAVED.",
                error.message || "Something went wrong. Please try again."
            );
        } finally {
            saveDraftButton.disabled = false;
        }
    });

    closeDraftSavedButton.addEventListener(
        "click",
        closeDraftSavedModal
    );

    draftSavedModal.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            event.preventDefault();
            closeDraftSavedModal();
        }

        if (event.key === "Tab") {
            event.preventDefault();
            closeDraftSavedButton.focus();
        }
    });
}