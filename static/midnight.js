getStats();

async function getStats() {
	const r = await fetch('activity');
	if (r.status != 200) {
		console.log('Could not load activity data.');
		return;
	}

	const d = JSON.parse(await r.text());
	drawPieChart(d);
	const list = document.querySelector('#projects');
	for (const k of Object.keys(d)) {
		const li = document.createElement('li');
		li.innerText = `${k}: ${formatAsTime(d[k])}`;
		li.classList.add(k);
		list.append(li);
	}

	addPathListeners();
}

function formatAsTime(sec) {
	sec = Number.parseInt(sec);
	return Math.floor(sec / 3600) > 0
		? `${Math.floor(sec / 3600)} hours`
		: `${Math.floor(sec / 60)} minutes`;
}

function leadingZero(n) {
	return toString(n).length == 1 ? `0${n}` : n;
}

function addPathListeners() {
	for (const element of document.querySelectorAll('path')) {
		element.addEventListener('mouseover', e => {
			document.querySelector(`li.${e.target.classList[0]}`).style
				.fontWeight = 'bold';
		});
		element.addEventListener('mouseleave', e => {
			document.querySelector(`li.${e.target.classList[0]}`).style
				.fontWeight = '';
		});
	}
}
