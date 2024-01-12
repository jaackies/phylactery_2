// Little script for the Membership Preview form.
// Prevents Navigation away from the page without confirmation from the browser.
// Doesn't work when hitting a submit button.

const beforeUnloadHandler = (event) => {
	// Recommended
	event.preventDefault();
	// Included for legacy support, e.g. Chrome/Edge < 119
	event.returnValue = true;
};

const submit_buttons = document.querySelectorAll("button[type='submit']");

for (i of submit_buttons) {
	i.addEventListener("click", (event) => {
		window.removeEventListener("beforeunload", beforeUnloadHandler);
		setTimeout(() => {
			window.addEventListener("beforeunload", beforeUnloadHandler);
		}, 100);
	});
}

window.addEventListener("beforeunload", beforeUnloadHandler);
