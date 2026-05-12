// site/js/main.js
const pages = document.querySelectorAll('.page');
const btns = document.querySelectorAll('.nav-btn');
function showPage(pageId) {
	pages.forEach(page => {
		page.classList.remove('active-page');
	});
	const activePage = document.getElementById(pageId);
	if(activePage) activePage.classList.add('active-page');

	btns.forEach(btn => {
		btn.classList.remove('active');
		if(btn.getAttribute('data-page') === pageId) {
			btn.classList.add('active');
		}
	});
}


btns.forEach(btn => {
	btn.addEventListener('click', () => {
		const pageId = btn.getAttribute('data-page');
		showPage(pageId);
	});
});
document.querySelector('[data-page="home"]').classList.add('active');