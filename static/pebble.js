const styles = ['*b*', '*i*', '*bi*', '*ib*'];
const pebble = {
	lines: [],
	head: 0,
	el: document.querySelector('#pebble-contents'),
	line() {
		return pebble.lines[pebble.head];
	},
	nextline() {
		return pebble.lines[pebble.head++];
	},
	style: [],
	type: {
		HEADER() {
			pebble_BASIC('h3');
		},
		NUMBERED_HEADER() {
			pebble_NUMBERED_HEADER();
		},
		LINK() {
			pebble_LINK();
		},
		LI() {
			pebble_LI();
		},
		RAW() {
			pebble_BASIC('pre');
		},
		UNK() {
			pebble_BASIC('p');
		},
	},
};

function renderPebble(s) {
	pebble.el.innerHTML = '';
	pebble.lines = s.split('\n').filter(e => e !== '');
	pebble.head = 0;
	while (pebble.line()) {
		addPebble();
		pebble.head++;
	}

	updateView('pebble');
}

function determineLineKind(e) {
	if (e == '-') {
		return 'HEADER';
	}

	if (e[0] == '-' && Number.parseInt(e[1])) {
		return 'NUMBERED_HEADER';
	}

	if (e == '->' && pebble.line().includes('@')) {
		return 'LINK';
	}

	if (e == '.') {
		return 'LI';
	}

	if (e == '-\\') {
		return 'RAW';
	}

	return 'UNK';
}

function addPebble() {
	const [identifier, content] = pebble.line().split(/ (.*)/s);
	const kind = determineLineKind(identifier);
	if (kind != 'UNK') {
		pebble.identifier = identifier;
		pebble.lines[pebble.head] = content;
	}

	styleLine();
	pebble.type[kind]();
}

function styleLine() {
	for (const s of styles) {
		if (pebble.line().includes(s)) {
			pebble.lines[pebble.head] = pebble.lines[pebble.head]
				.replace(s, '').trim();
			pebble.style = s.replaceAll('*', '').split('');
			return;
		}
	}

	pebble.style = [];
}

function addStyle(item) {
	for (const c of pebble.style) {
		item.classList.add(c);
	}
}

function pebble_BASIC(type) {
	const item = document.createElement(type);
	item.classList.add('pebble');
	addStyle(item);
	item.innerText = pebble.line();
	pebble.el.append(item);
}

function pebble_NUMBERED_HEADER() {
	const item = document.createElement(`h${pebble.identifier.split('')[1]}`);
	item.innerText = pebble.line();
	item.classList.add('pebble');
	pebble.el.append(item);
}

function pebble_LINK() {
	const p = pebble.line().split('@');
	const item = document.createElement('a');
	item.target = 'blank_';
	item.href = p[1];
	item.innerText = p[0];
	addStyle(item);
	item.classList.add('pebble');
	pebble.el.append(item);
}

function pebble_LI() {
	let id;
	const item = document.createElement('ul');
	item.classList.add('pebble');
	do {
		const li = document.createElement('li');
		li.innerText = pebble.line();
		li.classList.add('pebble');
		addStyle(li);
		item.append(li);
		id = pebble.line().split(' ')[0];
	} while (pebble.nextline() && determineLineKind(id) == 'LI');

	pebble.head--;
	pebble.el.append(item);
}
