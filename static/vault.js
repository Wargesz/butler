registerClickEvents();
indentNestedFolders();

document.querySelector('#viewer #toolbar button').addEventListener('click', () => {
    document.querySelector('#viewer').style.display = 'none';
});

function registerClickEvents() {
	for (const e of document.querySelectorAll('.file')) {
		e.addEventListener('click', async () => {
			path = getPathOfElement(e);
			const r = await fetch('file?' + new URLSearchParams({
                'path': `${path}/${e.innerText}`,
                'scope': e.classList.contains('private') ? 'private' : 'public',
            }));
			const text = await r.text();
			const element = document.querySelector('#viewer');
			element.style.display = 'block';
			document.querySelector('.opened-file').innerText = e.innerText;
            document.querySelector('#viewer-contents').innerText = text;
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
