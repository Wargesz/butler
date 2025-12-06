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

				if (targetId == 'edit-view') {
					const contents = document.querySelector('#viewer-contents');
					contents.value = context.content;
					context.content = '';
					updateView('view');
				}
			}
		}
	});
}

document.querySelector('#upload').addEventListener('click', async e => {
	clearActiveFile();
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

document.querySelector('#edit-content').addEventListener('click', e => {
	const content = document.querySelector('#viewer-contents');
	updateView('edit');
	context.content = content.value;
	content.readOnly = false;
	content.focus();
});

document.querySelector('#save-editing').addEventListener('click', async () => {
	const content = document.querySelector('#viewer-contents').value;
	if (content === context.content) {
		updateView('view');
		notify('No changes detected');
		return;
	}

	const r = await fetch('file', {
		method: 'POST',
		body: new URLSearchParams({
			content,
			path: context.path,
			scope: context.scope,
		}),
	});
	const res = await r.text();
	notify(res);
	updateView('view');
});

document.querySelector('#delete-file').addEventListener('click', async () => {
	const r = await fetch(`file?path=${context.path}&scope=${context.scope}`, {
		method: 'DELETE',
	});
	const text = await r.text();
	notify(text);
    updateView('browse');
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
			context.owner = fileInfo.owner;
			document.querySelector('#viewer-contents').readOnly = true;
			document.querySelector('.opened-file').innerText
                = fileInfo.file.split('/').at(-1);
			if (fileInfo.content) {
				document.querySelector('#viewer-contents').value
                    = fileInfo.content;
			} else {
				document.querySelector('#viewer-contents').placeholder
                    = 'Empty file';
				document.querySelector('#viewer-contents').value = '';
			}

			updateView('view');
		});
	}
}

function indentNestedFolders() {
	for (const e of document.querySelectorAll('.nested')) {
		const level = getNestedLevel(e) + 1;
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

	for (const id of elements) {
		document.querySelector(`#${id}`).style.display = 'none';
	}

	for (const id of views[context.view]) {
		document.querySelector(`#${id}`).style.display = 'block';
	}

	if (context.view === 'view') {
		document.querySelector('#viewer-contents').readOnly = true;
		document.querySelector('#edit-content').style.display
                = context.owner ? 'block' : 'none';
		document.querySelector('#delete-file').style.display
                = context.owner ? 'block' : 'none';
	}

	if (context.view === 'browse') {
		context.path = '';
		context.owner = '';
	}
}

function notify(message) {
	const n = document.querySelector('#notification');
	n.animate([
		{transform: 'translateX(100%)'},
		{transform: 'translateX(0)'},
	], {duration: 120});
	n.innerText = message;
	n.hidden = false;
	setTimeout(() => {
		n.animate([
			{transform: 'translateX(0)', opacity: 1},
			{transform: 'translateX(100%)', opacity: 0},
		], {duration: 120});
	}, 1580);
	setTimeout(() => {
		n.hidden = true;
	}, 1650);
}
