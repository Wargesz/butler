document.querySelector('#open-profile').addEventListener('click', () => {
	const settings = document.querySelector('#profile');
	settings.style.display = settings.style.display == 'none' ? 'block' : 'none';
});

document.querySelector('#api-key').addEventListener('click', e => {
	e.target.value = e.target.dataset.value;
});

document.querySelector('#profile').addEventListener('mouseout', () => {
	document.querySelector('#api-key').value = 'click to reveal';
});

function changeProjectFolder() {
	const input = document.querySelector('#home-folder');
	input.focus();
	input.toggleAttribute('readonly');
}

async function saveProjectFolder() {
	const input = document.querySelector('#home-folder');
	input.toggleAttribute('readonly');
	if (input.value == input.getAttribute('original-value')) {
		notify('No changes made');
		return;
	}

	const r = await fetch('user', {
		method: 'POST',
		body: new URLSearchParams({
			param: 'home-folder',
			value: input.value,
		}),
	});
	const j = JSON.parse(await r.text());
    input.setAttribute('original-value', input.value);
	notify(j.status);
}

async function generateNewKey() {
	const input = document.querySelector('#api-key');
	const r = await fetch('user', {
		method: 'POST',
		body: new URLSearchParams({
			param: 'api-key',
			value: input.dataset.value,
		}),
	});
	const j = JSON.parse(await r.text());
	input.dataset.value = j.value;
	notify(j.status);
}

function notify(message) {
	const n = document.querySelector('#notification');
	n.animate([
		{transform: 'translateX(0)'},
		{transform: 'translateX(100%)'},
	], {duration: 120});
	n.innerText = message;
	n.hidden = false;
	setTimeout(() => {
		n.animate([
			{transform: 'translateX(100%)', opacity: 1},
			{transform: 'translateX(0)', opacity: 0},
		], {duration: 120});
	}, 1580);
	setTimeout(() => {
		n.hidden = true;
	}, 1650);
}
