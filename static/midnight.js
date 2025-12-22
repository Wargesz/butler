getStats();

async function getStats() {
	const r = await fetch('activity');
	if (r.status != 200) {
		console.log('Could not load activity data.');
		return;
	}

	const d = JSON.parse(await r.text());
	drawPieChart(Object.keys(d).map(k => d[k]));
	const list = document.querySelector('#projects');
	for (const k of Object.keys(d)) {
		const li = document.createElement('li');
		li.innerText = `${k}: ${formatAsTime(d[k])}`;
		list.append(li);
	}
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
