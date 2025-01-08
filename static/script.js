const dropdowns = document.querySelectorAll(".dropdown");

dropdowns.forEach((dropdown) => {
	const select = dropdown.querySelector(".select");
	const caret = dropdown.querySelector(".caret");
	const menu = dropdown.querySelector(".menu");
	const options = dropdown.querySelectorAll(".menu li");
	const selected = dropdown.querySelector(".selected");

	dropdown.addEventListener("click", (e) => {
		select.classList.toggle("select-clicked");
		caret.classList.toggle("caret-rotate");
		menu.classList.toggle("menu-open");
	});

	options.forEach((option) => {
		option.addEventListener("click", () => {
			selected.innerText = option.innerText;
			e.stopPropagation();
			select.classList.remove("select-clicked");
			caret.classList.remove("caret-rotate");
			menu.classList.remove("menu-open");
			options.forEach((option) => {
				option.classList.remove("active");
			});
			option.classList.add("active");
		});
	});
});
const container = document.querySelector(".container");
window.addEventListener("load", () => {});

const submit = document.querySelector(".submit");
const help = document.querySelector(".container-main");
const inputPrompt = document.getElementById("prompt");
const loadingBar = document.querySelector(".loading-bar");

function startLoading() {
	loadingBar.classList.add("loading");
}

function stopLoading() {
	loadingBar.classList.remove("loading");
}

inputPrompt.addEventListener("keydown", (event) => {
	if (event.key === "Enter") {
		Enter();
	}
});

submit.addEventListener("click", Enter);
function Enter() {
	help.parentNode.removeChild(help);
}
const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const mainContent = document.getElementById("mainContent");
const navbar = document.querySelector(".container");
// Handle sidebar toggle
sidebarToggle.addEventListener("click", () => {
	sidebar.classList.toggle("active");
	mainContent.classList.toggle("shifted");
	navbar.classList.toggle("shifted"); // Shift the navbar as well
});
