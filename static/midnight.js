getStats();
hideAllViews();
setContext('total');

async function getStats() {
	const r = await fetch('activity?tab=total');
	if (r.status != 200) {
		console.log('Could not load activity data.');
		return;
	}

	const d = JSON.parse(await r.text());
	context.data = d;
	loadTotalProjectData(d);
	renderTotalHeatMap(d.heatmap);
	loadProjectSelector(d.time);
	addPathListeners();
}

function loadTotalProjectData(d) {
	drawChartTimeData(d.time, '#projects-svg', '#total #projects ol#entries');
	drawChartTimeData(d.editor, '#editor-svg', '#total #editors ol#entries');
}

function drawChartTimeData(d, chartTarget, infoTarget) {
	const sorted = sortByTime(d);
	drawPieChart(sorted, chartTarget);
	const list = document.querySelector(infoTarget);
	for (const k of Object.keys(sorted)) {
		const li = document.createElement('li');
		li.innerText = `${k}: ${formatAsTime(sorted[k])}`;
		li.classList.add(cleanPath(k));
		li.addEventListener('mouseover', () => {
			document.querySelector(`path.${k}`).classList.toggle('selected');
		});
		li.addEventListener('mouseout', () => {
			document.querySelector(`path.${k}`).classList.toggle('selected');
		});
		li.addEventListener('click', () => {
			document.querySelector(`select [value='${k}']`).selected = true;
			setContext('project', k);
		});
		list.append(li);
	}
}

function loadProjectSelector(d) {
	const select = document.querySelector('#project select');
	for (const k of Object.keys(d)) {
		const option = document.createElement('option');
		option.value = k;
		option.innerText = k;
		select.append(option);
	}
}

async function getProjectStats() {
	const r = await fetch(`activity?tab=project&project=${context.project}`);
	if (r.status != 200) {
		console.log('Could not load activity data.');
	}

	const d = JSON.parse(await r.text());
	renderProjectTime(d.time);
	renderProjectHeatMap(d.heatmap);
}

function renderHeatMap(d, target) {
	const date = new Date();
	date.setDate(date.getDate() - 364);
	const table = document.querySelector(target);
	table.innerHTML = '';
	for (let i = 0; i < 52; i++) {
		const row = document.createElement('tr');
		for (let o = 0; o < 7; o++) {
			const cell = document.createElement('td');
			cell.title = date.toDateString();
			cell.classList.add(`date-${date.getFullYear()}-${leadingZero(date.getMonth() + 1)}-${leadingZero(date.getDate())}`);
			date.setDate(date.getDate() + 1);
			row.append(cell);
		}

		table.append(row);
	}

	for (const k of Object.keys(d)) {
		const cell = document.querySelector(`${target} .date-${k}`);
		cell.style.backgroundColor = '#3DAC78';
	}
}

function renderTotalHeatMap(d) {
	renderHeatMap(d, '#total #heatmap');
}

function renderProjectHeatMap(d) {
	renderHeatMap(d, '#project #heatmap');
}

function renderProjectTime(d) {
	const list = document.querySelector('#project ol');
	list.innerHTML = '';
	for (const k of Object.keys(d)) {
		const li = document.createElement('li');
		li.innerText = `${k}: ${formatAsTime(d[k])}`;
		li.classList.add(cleanPath(k));
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
	const s = String(n);
	if (s.length == 1) {
		return `0${s}`;
	}

	return s;
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

document.querySelector('span#project select').addEventListener('change', e => {
	const select = e.target;
	setProject(select.value);
});

function sortByTime(d) {
	return Object.fromEntries(Object.entries(d).sort((a, b) => (b[1] - a[1])));
}

function setContext(tab, project) {
	context.tab = tab;
	if (project) {
		context.project = project;
	}

	updateView();
}

function setProject(project) {
	context.project = project;
	updateView();
}

function updateView() {
	hideAllViews();
	switch (context.tab) {
		case 'total': {
			document.querySelector('#total').style.display = 'block';
			break;
		}

		case 'project': {
            if (!context.project) {
                context.project = document.querySelector('select option').value;
            }
			getProjectStats();
			document.querySelector('#project').style.display = 'block';
			break;
		}
	}
}

function hideAllViews() {
	for (const v of context.views) {
		document.querySelector(`#${v}`).style.display = 'none';
	}
}

function cleanPath(path) {
	return path.replaceAll('/', '_').replaceAll('.', '-');
}
