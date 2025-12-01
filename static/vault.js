registerClickEvents();
indentNestedFolders();

for (const element of document.querySelectorAll('button.close')) {
	element.addEventListener('click', e => {
		for (const c of e.target.classList) {
			if (c.startsWith('close-target-')) {
				const targetId = c.split('close-target-')[1];
				if (targetId == 'viewer') {
					clearActiveFile();
					updateView('browse');
				}

				if (targetId == 'uploader') {
					updateView('browse');
				}
			}
		}
	});
}

document.querySelector('#upload').addEventListener('click', async e => {
    updateView('upload');
	const r = await fetch('paths', {
		headers: {
			Accept: 'application/json',
		},
	});
	const text = await r.text();
	const paths = JSON.parse(text);
	const select = document.querySelector('#upload-path');
	select.innerHTML = '';
	let option = document.createElement('option');
	option.disabled = true;
	option.innerText = 'Public';
	select.append(option);
	for (const p of paths.public) {
		option = document.createElement('option');
		option.innerText = p;
		option.value = `PUBLIC:${p}`;
		select.append(option);
	}

	option = document.createElement('option');
	option.disabled = true;
	option.innerText = 'Private';
	select.append(option);
	for (const p of paths.private) {
		option = document.createElement('option');
		option.innerText = p;
		option.value = `PRIVATE:${p}`;
		select.append(option);
	}
});

document.querySelector('#files').addEventListener('change', e => {
	const files = e.target;
	const p = document.querySelector('pre#selected-files');
	p.innerText = '';
	for (const f of files.files) {
		p.innerText += `${f.name}\n`;
	}
});

document.querySelector('.edit-content').addEventListener('click', e => {
	const content = document.querySelector('#viewer-contents');
    updateView('edit');
	content.readOnly = false;
	content.focus();
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
			const text = await r.text();
			const fileInfo = JSON.parse(text);
			context.path = fileInfo.file;
			context.scope = fileInfo.scope;
            updateView('view');
			document.querySelector('.edit-content').hidden = !fileInfo.owner;
			document.querySelector('#viewer-contents').readOnly = true;
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

function updateView(newValue) {
	if (newValue) {
		context.view = newValue;
	}

	for (const key in views[context.view]) {
		document.querySelector(`#${key}`).style.display
            = views[context.view][key] ? 'none' : 'block';
	}
}
