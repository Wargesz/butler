const svgs = document.querySelector('#svgs');
const letters = '0123456789ABCDEF';
const xmlnsString = 'http://www.w3.org/2000/svg';
const size = 150;
const origo = '0 0';

function drawPieChart(values) {
	clear();
	const n = calculateSlices(Object.values(values));
	let offset = 0;
	let i = 0;
	for (const element of n) {
		const c = genRandomColor();
		const start = getCoords(offset).join(' ');
		const end = getCoords(offset + element).join(' ');
		const largeArc = element >= 0.5 ? '1' : '0';
		const reverse = element - 0.5 < 0.25 || element - 0.5 > -0.25 ? '1' : '0';
		const path = document.createElementNS(xmlnsString, 'path');
		const dString = `M ${origo} L ${start} A ${size},${size} 0 ${largeArc} ${reverse} ${end} L ${origo} Z`;
		path.setAttribute('d', dString);
		path.setAttribute('fill', c);
		path.classList.add(Object.keys(values)[i]);
		path.style.opacity = '85%';
		path.addEventListener('mouseover', () => {});
		offset += element;
		svgs.append(path);
		i++;
	}
}

function calculateSlices(n) {
	// N = [30,40,50] -> [%,%,%]
	// calculating slices
	sum = 0;
	for (const i of n) {
		sum += i;
	}

	for (let i = 0; i < n.length; i++) {
		n[i] /= sum;
	}

	return n;
}

function getCoords(rad) {
	rad *= Math.PI * 2;
	rad += Math.PI / 4;
	return [size * Math.sin(rad), -size * Math.cos(rad)];
}

function clear() {
	svgs.innerHTML = '';
}

function genRandomColor() {
	let code = '#';
	for (let i = 0; i < 6; i++) {
		code += letters[Math.floor(Math.random() * 16)];
	}

	return code;
}
