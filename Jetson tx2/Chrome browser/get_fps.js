const times = [];
let fps;


requestAnimationFrame(function loop(){
	const now = performance.now();
	while (times.length > 0 && times[0] <= now - 1000) {
		times.shift();
	}
	times.push(now);
	fps = times.length;
	console.log(fps);
	requestAnimationFrame(loop)
})
