registerClickEvents();
indentNestedFolders();

document.querySelector('#viewer #toolbar .close').addEventListener('click', e => {
	clearActiveFile();
	document.querySelector('#viewer').style.display = 'none';
});

function registerClickEvents() {
	for (const e of document.querySelectorAll('.file')) {
		e.addEventListener('click', async () => {
			clearActiveFile();
			e.classList.add('active-file');
			path = getPathOfElement(e);
			const r = await fetch('file?' + new URLSearchParams({
				path: `${path}/${e.innerText}`,
				scope: e.classList.contains('private') ? 'private' : 'public',
			}), {
				headers: {
					Accept: 'application/json',
				},
			});
			context.path = `${path}/${e.innerText}`;
			const text = await r.text();
			const fileInfo = JSON.parse(text);
			context.path = fileInfo.file;
			const element = document.querySelector('#viewer');
			element.style.display = 'block';
			document.querySelector('.opened-file').innerText = fileInfo.file.split('/').at(-1);
			if (fileInfo.content == '') {
				document.querySelector('#viewer-contents').placeholder = 'Empty file';
				document.querySelector('#viewer-contents').value = '';
			} else {
				document.querySelector('#viewer-contents').value = fileInfo.content;
			}
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

function clearActiveFile() {
	for (const e of document.querySelectorAll('.active-file')) {
		e.classList.remove('active-file');
	}
}
