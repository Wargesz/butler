const topC = [61, 172, 120];
const botC = [68, 68, 68];
const thresholdC = 10;
hideAllViews();
getStats().then(() => {
	setContext('total');
});

async function getStats() {
	const r = await fetch('activity?tab=total');
	if (r.status != 200) {
		console.log('Could not load activity data.');
		return;
	}

	const d = JSON.parse(await r.text());
	context.data = d;
	loadTotalProjectData(d);
	renderHeatMap(d.heatmap);
	loadProjectSelector(d.time);
	addPathListeners();
}

function loadTotalProjectData(d) {
	drawChartTimeData(d.time, '#projects-svg', '#total #projects ol#entries', true, 10);
	drawChartTimeData(d.editor, '#editor-svg', '#total #editors ol#entries', false, 10);
}

function drawChartTimeData(d, chartTarget, infoTarget, redirect, limit) {
	const sorted = sortByTime(d);
    const keys = Object.keys(sorted).slice(0, 10);
    const values = {};
    for (const k of keys) {
        values[k] = sorted[k];
    }
	drawPieChart(values, chartTarget);
	const list = document.querySelector(infoTarget);
	for (const k of Object.keys(sorted).slice(0, limit || Object.keys(sorted).length)) {
		const li = document.createElement('li');
		li.innerText = `${k}: ${formatAsTime(sorted[k])}`;
		li.classList.add(cleanPath(k));
		li.addEventListener('mouseover', () => {
			document.querySelector(`path.${k}`).classList.toggle('selected');
		});
		li.addEventListener('mouseout', () => {
			document.querySelector(`path.${k}`).classList.toggle('selected');
		});
		if (redirect) {
			li.addEventListener('click', () => {
				openProjectTab(k);
			});
		}

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
	renderHeatMap(d.heatmap);
}

function renderHeatMap(d) {
	const date = new Date();
	date.setDate(date.getDate() - 363);
	const table = document.querySelector('table#heatmap');
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
		const cell = document.querySelector(`table#heatmap .date-${k}`);
		const value = Math.min(d[k] / thresholdC, 1);
		const c = [];
		for (let i = 0; i < 3; i++) {
			c.push(botC[i] + (topC[i] - botC[i]) * value);
		}

		cell.classList.add(`files-${d[k]}`);
		cell.style.backgroundColor = `rgb(${c.join(',')})`;
	}
}

function openProjectTab(project) {
	document.querySelector(`select [value='${project}']`).selected = true;
	setContext('project', project);
}

function renderProjectTime(d) {
	const list = document.querySelector('#project ol');
	list.innerHTML = '';
	files = Object.entries(d).sort((a, b) => a[0].split('/').length - b[0].split('/').length);
	const depth = -1;
	const tree = generateTree(files);
	drawTree(tree, list, depth);
}

function drawTree(tree, parentElement, depth) {
	depth++;
	for (const k of Object.keys(tree)) {
		const li = document.createElement('li');
		if (tree[k].time) {
			let span = document.createElement('span');
			span.innerText = k;
			li.append(span);
			span = document.createElement('span');
			span.style.textAlign = 'right';
			span.innerText = formatAsTime(tree[k].time);
			li.append(span);
		} else {
			li.innerText = '📁 ' + k + '/';
		}

		li.style.marginLeft = depth + 'em';
		parentElement.append(li);
		if (tree[k].time) {
			continue;
		}

		drawTree(tree[k], parentElement, depth);
	}
}

function generateTree(d) {
	const tree = {};
	for (const [file, time] of d) {
		const path = file.split('/');
		let head = tree;
		for (const p of path) {
			head[p] ||= {};
			head = head[p];
		}

		head.time = time;
	}

	return tree;
}

function formatAsTime(sec) {
	sec = Number.parseInt(sec);
	if (sec < 60) {
		return sec + ' seconds';
	}

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
				.textShadow = '0px 0px 1px white';
		});
		element.addEventListener('mouseleave', e => {
			document.querySelector(`li.${e.target.classList[0]}`).style
				.textShadow = '';
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
			renderHeatMap(context.data.heatmap);
			document.querySelector('#total').style.display = 'block';
			break;
		}

		case 'project': {
			context.project ||= document.querySelector('select option').value;

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
