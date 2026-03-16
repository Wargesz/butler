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
	loadStats();
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

function loadStats() {
	const month = context.data.stats.month.split('|');
	const d = new Date(month[0]);
	document.querySelector('#total #stats #month').innerText = `${d.toLocaleString('default', {month: 'long', year: 'numeric'})}:\n${formatAsTime(month[1])}`;
	document.querySelector('#total #stats #month').addEventListener('click', () => {
		const end = new Date(month[0].split('-')[0], month[0].split('-')[1], 1);
		console.log(month, `${month[0]}-1`, end.toISOString().split('T')[0]);
		updateCalendar(`${month[0]}-01`, end.toISOString().split('T')[0]);
		setContext('calendar');
	});
	const week = context.data.stats.week.split('|');
	const monday = document.querySelector(`td.date-${week[0]}`).parentElement.querySelector('td:first-of-type').className.split(' ')[0].split('date-')[1];
	const sunday = document.querySelector(`td.date-${week[0]}`).parentElement.querySelector('td:last-of-type').className.split(' ')[0].split('date-')[1];
	document.querySelector('#total #stats #week').innerText = `${monday}-${sunday.split('-')[2]}:\n ${formatAsTime(week[1])}`;
	document.querySelector('#total #stats #week').addEventListener('click', () => {
		updateCalendar(monday, sunday);
		setContext('calendar');
	});
	const day = context.data.stats.day.split('|');
	document.querySelector('#total #stats #day').innerText = `${day[0]}:\n${formatAsTime(day[1])}`;
	document.querySelector('#total #stats #day').addEventListener('click', () => {
		updateCalendar(day[0], day[0]);
		setContext('calendar');
	});
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
	date.setDate(date.getDate() - date.getDay() + 1);
	date.setDate(date.getDate() - 51 * 7);
	const table = document.querySelector('table#heatmap');
	table.innerHTML = '';
	let month = date.getMonth();
	for (let i = 0; i < 52; i++) {
		const row = document.createElement('tr');
		const weeklyAvg = document.createElement('th');
		weeklyAvg.innerText = '';
		row.append(weeklyAvg);
		for (let o = 0; o < 7; o++) {
			const cell = document.createElement('td');
			cell.title = date.toDateString();
			const dateString = `${date.getFullYear()}-${leadingZero(date.getMonth() + 1)}-${leadingZero(date.getDate())}`;
			cell.classList.add(`date-${dateString}`);
			if (date.getMonth() % 2) {
				cell.classList.add('alt-month');
			}

			cell.addEventListener('click', () => {
				updateCalendar(dateString, dateString);
				setContext('calendar');
			});
			date.setDate(date.getDate() + 1);
			row.append(cell);
		}

		if (month != getMonthFromDateClass(row.lastChild)) {
			month = getMonthFromDateClass(row.lastChild);
			const header = document.createElement('th');
			header.innerText = row.lastChild.title.split(' ')[1];
			const lastCell = row.lastChild;
			row.append(header);
			const cellDate = lastCell.className.split('-');
			const scopeYear = cellDate[1];
			const scopeMonth = cellDate[2];
			const lastDay = new Date(scopeYear, scopeMonth, 1);
			header.addEventListener('click', () => {
				updateCalendar(`${scopeYear}-${scopeMonth}-01`, lastDay.toISOString().split('T')[0]);
				setContext('calendar');
			});
		}

		table.append(row);
	}

	for (const k of Object.keys(d.days)) {
		const cell = document.querySelector(`table#heatmap .date-${k}`);
		const value = Math.min(d.days[k] / thresholdC, 1);
		const c = [];
		for (let i = 0; i < 3; i++) {
			c.push(botC[i] + (topC[i] - botC[i]) * value);
		}

		cell.classList.add(`files-${d.days[k]}`);
		cell.style.backgroundColor = `rgb(${c.join(',')})`;
	}

	for (const k of Object.keys(d.weeks)) {
		const rowHeader = document.querySelector(`.date-${k}`).parentElement.querySelector('th');
		const monday = rowHeader.nextSibling.className.split(' ')[0].split('date-')[1];
		const sunday = (rowHeader.parentElement.lastChild.nodeName == 'TH'
			? rowHeader.parentElement.lastChild.previousSibling
			: rowHeader.parentElement.lastChild).className.split(' ')[0].split('date-')[1];
		date.setDate(date.getDate() + 6);
		rowHeader.addEventListener('click', () => {
			updateCalendar(monday, sunday);
			setContext('calendar');
		});
		rowHeader.innerText = formatAsClock(d.weeks[k]);
	}
}

function getMonthFromDateClass(e) {
	return Number.parseInt(e.className.split('-')[2]);
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

		li.style.marginLeft = `${depth}em`;
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

async function updateCalendar(newFrom, newTo) {
	const fromInput = document.querySelector('#calendar input#from');
	if (newFrom) {
		fromInput.value = newFrom;
	}

	const toInput = document.querySelector('#calendar input#to');
	if (newTo) {
		toInput.value = newTo;
	}

	const r = await fetch(`activity?tab=calendar&from=${fromInput.value}&to=${toInput.value}`);
	const d = JSON.parse(await r.text());
	const list = document.querySelector('#calendar ol');
	list.innerHTML = '';
	files = Object.entries(d).sort((a, b) => a[0].split('/').length - b[0].split('/').length);
	const depth = -1;
	const tree = generateTree(files);
	drawTree(tree, list, depth);
}

function formatAsTime(sec) {
	sec = Number.parseInt(sec);
	if (sec < 60) {
		return sec + ' second' + (sec > 1 ? 's' : '');
	}

	return Math.floor(sec / 3600) > 0
		? `${Math.floor(sec / 3600)} hour${+Math.floor(sec / 3600) > 1 ? 's' : ''}`
		: `${Math.floor(sec / 60)} minute${+Math.floor(sec / 60) > 1 ? 's' : ''}`;
}

function formatAsClock(sec) {
	const h = Math.floor(sec / 60 / 60);
	const m = Math.floor(sec / 60 % 60);
	const s = Math.floor(sec % 60);
	return `${leadingZero(h)}:${leadingZero(m)}:${leadingZero(s)}`;
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

for (const e of document.querySelectorAll('#calendar input[type=date]')) {
	e.addEventListener('change', () => {
		/*
		Const from = new Date(document.querySelector('#calendar input#from').value);
		const to = new Date(document.querySelector('#calendar input#to').value);
        if (from > to || to < from) {
            [from.value, to.value] = [to.value, from.value];
            console.log('swap');
        }
        */
		updateCalendar();
	});
}

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
			{
				renderHeatMap(context.data.heatmap);
				document.querySelector('#total').style.display = 'block';
				break;
			}
		}

		case 'project': {
			{
				context.project ||= document.querySelector('select option').value;

				getProjectStats();
				document.querySelector('#project').style.display = 'block';
				break;
			}
		}

		case 'calendar': {
			renderHeatMap(context.data.heatmap);
			document.querySelector('#calendar').style.display = 'block';
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
