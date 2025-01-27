// Script for the membership form
// Shows / Hides the relevant fields based on which option is selected.

const checkPaymentMethod = () => {
	const cash_button = document.querySelector("input[name='preview-cash_or_transfer'][value='cash']");
	const transfer_button = document.querySelector("input[name='preview-cash_or_transfer'][value='transfer']");
	const transfer_panel = document.querySelector("#reference-code-card");
	const checklist_panel = document.querySelector("#checklist-card");
	const payment_text = document.querySelector("#payment_method_text");
	let show_transfer_panel = false;
	let show_checklist_panel = false;

	if (cash_button.checked) {
		show_transfer_panel = false;
		show_checklist_panel = true;
		payment_text.textContent = " in cash"
	}
	else if (transfer_button.checked) {
		show_transfer_panel = true;
		show_checklist_panel = true;
		payment_text.textContent = " via bank transfer"
	}
	else {
		show_transfer_panel = false;
		show_checklist_panel = false;
		payment_text.textContent = "";
	}

	if (show_transfer_panel) {
		transfer_panel.classList.remove("d-none");
	}
	else {
		transfer_panel.classList.add("d-none");
	}

	if (show_checklist_panel) {
		checklist_panel.classList.remove("d-none");
	}
	else {
		checklist_panel.classList.add("d-none");
	}

}

document.addEventListener("DOMContentLoaded", function() {
	document.querySelector("input[name='preview-cash_or_transfer'][value='cash']").addEventListener("change", checkPaymentMethod);
	document.querySelector("input[name='preview-cash_or_transfer'][value='transfer']").addEventListener("change", checkPaymentMethod);
	checkPaymentMethod();
});