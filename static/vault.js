function registerClickEvents() {
	for (const e of document.querySelectorAll('.pocket')) {
		e.addEventListener('click', async () => {
			path = getPathOfElement(e);
			const r = await fetch(`file?path=${path}`);
			const text = await r.text();
			const element = document.querySelector('#viewer');
			element.innerText = text;
            element.style.display = 'block';
		});
	}
}

registerClickEvents();

function getPathOfElement(e) {
	for (const c of e.classList) {
		if (c.startsWith('path-')) {
			return c.split('path-')[1];
		}
	}
}
