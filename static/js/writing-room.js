const letterBody = document.getElementById("letter-body");
const characterCount = document.getElementById("letter-character-count");

if (letterBody && characterCount) {
    function updateCharacterCount() {
        const count = letterBody.value.length;
        characterCount.textContent =
            `${count} ${count === 1 ? "character" : "characters"}`;
    }

    letterBody.addEventListener("input", updateCharacterCount);
    updateCharacterCount();
}

const clearLetterButton = document.getElementById("clear-letter");
const letterTitle = document.getElementById("letter-title");
const letterRecipient = document.getElementById("letter-recipient");

const letterModal = document.getElementById("letter-modal");
const cancelClearLetter = document.getElementById("cancel-clear-letter");
const confirmClearLetter = document.getElementById("confirm-clear-letter");

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
    
    letterModal.addEventListener("keydown", function (event) {
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

        if (event.key === "Escape") {
            event.preventDefault();
            closeClearModal();
            return;
        }

        if (event.key === "Tab") {
            const firstButton = cancelClearLetter;
            const lastButton = confirmClearLetter;

            if (event.shiftKey && document.activeElement === firstButton) {
                event.preventDefault();
                lastButton.focus();
            } else if (
                !event.shiftKey &&
                document.activeElement === lastButton
            ) {
                event.preventDefault();
                firstButton.focus();
            }
        }
    });

    cancelClearLetter.addEventListener("click", closeClearModal);

    confirmClearLetter.addEventListener("click", function () {
        letterTitle.value = "";
        letterRecipient.value = "";
        letterBody.value = "";

        letterBody.dispatchEvent(new Event("input", { bubbles: true }));

        closeClearModal();
    });
}
