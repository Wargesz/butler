registerClickEvents();
indentNestedFolders();

function registerClickEvents() {
	for (const e of document.querySelectorAll('.file')) {
		e.addEventListener('click', async () => {
			path = getPathOfElement(e);
			const r = await fetch(`file?path=${path}/${e.innerText}`);
			const text = await r.text();
			const element = document.querySelector('#viewer');
			element.innerText = text;
			element.style.display = 'block';
		});
	}
}

function indentNestedFolders() {
	for (const e of document.querySelectorAll('.nested')) {
		const level = getNestedLevel(e);
		e.style.marginLeft = `${level}em`;
	}
}

function getPathOfElement(e) {
	for (const c of e.classList) {
		if (c.startsWith('path-')) {
			return c.split('path-')[1];
		}
	}
}

function getNestedLevel(e) {
	for (const c of e.classList) {
		if (c.startsWith('nested-')) {
			return Number.parseInt(c.split('nested-')[1]);
		}
	}
}
