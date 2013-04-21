var ctx; var canvas;
var lives; var level; var score;
highscore = 0; 		//will have to account for this
image_tracker = []; //content in the form of [[image, xy coords]*number of images in track, speed] 
var W; var H;
var animationIntervalId;
var dead_flag = 0;

var medlog, biglog, shortlog;
var truck, racer, pinkcar, yellowcar, tractor;
var frog;

sprites = new Image(); sprites.src = 'assets/frogger_sprites.png';
dead	= new Image(); dead.src = 'assets/dead_frog.png';

//-------------------------
//  IMAGE OBJECT FUNCTIONS
//-------------------------
function draw_image(){
	ctx.drawImage(sprites, this.sx,this.sy,
				  this.swidth,this.sheight,
				  this.imx,this.imy,this.swidth, this.sheight);
};

function imageObj(sx,sy,sw,sh){
//IMAGE OBJECT CONSTRUCTOR
	this.sx = sx || 0;
	this.sy = sy || 0;
	this.swidth = sw || 0;
	this.sheight = sh || 0;
	this.imx = 0;
	this.imy = 0;
	this.make = draw_image;
};

//-------------------------
//DRAW THE BACKGROUND IMAGE
//-------------------------
function roadsides(posY){
	//function for drawing roadsides
	H_roadsides = 40;
	//draw orange line under border of image
	ctx.beginPath();
	ctx.moveTo(0, posY+5);
	ctx.lineTo(W, posY+5);
	ctx.lineWidth = 2;
	ctx.strokeStyle = '#cb630a';
	ctx.stroke();
	//draw orange line under border of image
	ctx.beginPath();
	ctx.moveTo(0, posY+H_roadsides-3);
	ctx.lineTo(W, posY+H_roadsides-3);
	ctx.lineWidth = 2;
	ctx.strokeStyle = '#cb630a';
	ctx.stroke();	
};

function background(){
	//WATER
	H_water = 290;
	ctx.fillStyle = "#191970";
	ctx.fillRect(0,0,W, H_water);
	
	//HEADER
	ctx.drawImage(sprites,0,0,W,110,0,0,W,110);
	
	//ROAD
	H_road = H - H_water;
	ctx.fillStyle = "#000000";
	ctx.fillRect(0,290,W, H_road);
	
	//ROADSIDES
	roadsides(265);
	roadsides(480);
	ctx.drawImage(sprites,0,115,W,40,0,265,W,40);
	ctx.drawImage(sprites,0,115,W,40,0,480,W,40);

	//FOOTER
	footer = 520; 
	//lives
	for (i = 0; i < lives; i += 1) {
		ctx.drawImage(sprites,12,330,30,30,i*20,footer,20,20);
	}
	//level
	ctx.fillStyle    = '#00FF00';
    ctx.font         = 'Bold 20px Sans-Serif';
    ctx.textBaseline = 'top';
    ctx.fillText  ('Level '+level, 70, footer);	
	//score & highscore
	ctx.font 	= 'Bold 15px Sans-Serif';
	ctx.fillText  ('Score: '+score,0,footer+20); 
	ctx.fillText  ('Highscore: '+highscore,150,footer+20);

};

//-------------------------
//    INITIAL DATA
//-------------------------
function frogdeath(){
	lives -= 1;
	dead_flag = 0;
	clearInterval(animationIntervalId);
	level_init();	
}

function animate(){
	ctx.clearRect(0,0,W,H); //reset canvas	
	background();
	
	for(t = 0; t < image_tracker.length; t++){
		for(i = 0;  i < image_tracker[t]['x'].length; i++){
			image_tracker[t]['x'][i] += image_tracker[t].speed;
			myx = image_tracker[t]['x'][i];
			if ((myx > W) && (Math.abs(image_tracker[t].speed)/image_tracker[t].speed == 1)){
				image_tracker[t]['x'][i] = -image_tracker[t].image.swidth;
			} 
			if((myx + image_tracker[t].image.swidth < 0) && (Math.abs(image_tracker[t].speed)/image_tracker[t].speed == -1)){
				image_tracker[t]['x'][i] = W+image_tracker[t].image.swidth;
			}
			image_tracker[t]['image'].imy = image_tracker[t].y;
			myx = image_tracker[t]['x'][i];
			image_tracker[t].image.imx = myx;
			if((t < 10) && (t >= 5)){ 
				collision_detection(myx, image_tracker[t].image.sx, t);
			}
			if((myx <= W+image_tracker[t].image.swidth) && (myx >= -image_tracker[t].image.swidth)){
				if((t == 10) && dead_flag){
					if(dead_flag == 20){ 
						frogdeath();
					}
					else {
						ctx.drawImage(dead,0,0,30,30,frog.imx,frog.imy,
									  5*dead_flag,5*dead_flag);
						dead_flag += 1;
					}				
				}
				else {
					image_tracker[t].image.make();
				}
			}			
		}
	}		
}

function game_over(){
//	while(true){
//		ctx.clearRect(0,0,W,H);	
//		console.log('GAME OVER!');		
//	}
}

function collision_detection(imgx,wid,t){
	if((t < 10) && (t >= 5)){  
		if((frog.imx >= imgx) && (frog.imx <= (imgx+wid))){
			if((frog.imy >= image_tracker[t].y) && (frog.imy <= (image_tracker[t].y+image_tracker[t].image.sheight))){
				dead_flag = 1;
				ctx.drawImage(dead,0,0,30,30,frog.imx,frog.imy,5,5);
			}
		}
	} else {
		if((frog.imx < imgx) || (frog.imx > (imgx+wid))){
			if((frog.imy >= image_tracker[t].y) && (frog.imy <= (image_tracker[t].y+image_tracker[t].image.sheight))){
				dead_flag = 1;
				ctx.drawImage(dead,0,0,30,30,frog.imx,frog.imy,5,5);
			}
		}
	}
}

function level_init(){
	level += 1;

	//set up image "tracks" (image_tracker) 	
	image_tracker[0]  = {'image': medlog, 'x': [-medlog.swidth, -((-5*medlog.swidth+W)/4), -((3*W - medlog.swidth)/4)], 'y': 120, 'speed': 2};
	image_tracker[1]  = {'image': pinkcar, 'x': [W+pinkcar.swidth, W+5*pinkcar.swidth, W+8*pinkcar.swidth, W+12*pinkcar.swidth], 'y': 150, 'speed': -2};
	image_tracker[2]  = {'image': biglog, 'x': [-biglog.swidth-30, -(2*biglog.swidth+10+2*W/3-2*medlog.swidth), -(3*biglog.swidth+W-3*medlog.swidth)], 'y': 180, 'speed': 3};
	image_tracker[3]  = {'image': shortlog, 'x':  [-W, -W/2+(shortlog.swidth - medlog.swidth), -W + 2*shortlog.swidth+medlog.swidth], 'y': 240, 'speed': 1};
	image_tracker[4]  = {'image': pinkcar, 'x': [W+pinkcar.swidth, W+5*pinkcar.swidth, W+8*pinkcar.swidth, W+12*pinkcar.swidth], 'y': 210, 'speed': -2};
	image_tracker[5]  = {'image': truck, 'x': [W+truck.swidth, W+5*truck.swidth/2], 'y': 330, 'speed': -1};
	image_tracker[6]  = {'image': racer, 'x': [-racer.swidth-30, -(10+2*W/3), -(2*W/3+10+racer.swidth*2)], 'y': 360, 'speed': 3};
	image_tracker[7]  = {'image': pinkcar, 'x': [W+pinkcar.swidth, W+5*pinkcar.swidth, W+8*pinkcar.swidth], 'y': 390, 'speed': -2};
	image_tracker[8]  = {'image': tractor, 'x': [-tractor.swidth, -(5*tractor.swidth), -(9*tractor.swidth)], 'y': 420, 'speed': 1};		
	image_tracker[9]  = {'image': yellowcar, 'x': [W+2*yellowcar.swidth, W+5*pinkcar.swidth, W+8*pinkcar.swidth], 'y': 450, 'speed': -2};
	image_tracker[10] = {'image':frog, 'x': [W/2-50], 'y': 485, 'speed':0};
	animationIntervalId = setInterval(animate, 30);
	
	if(level == 2){
		(image_tracker[1]['x']).splice(3,3);
		image_tracker[4]['x'].splice(6-level,6-level);
		image_tracker[6].speed = image_tracker[6].speed*2;
		image_tracker[8]['x'].push(-(13*tractor.swidth));
	}
	else if(level == 3){
		image_tracker[0].speed = image_tracker[0].speed/2;
		image_tracker[2]['x'].splice(2,2);
		image_tracker[4]['x'].splice(6-level,6-level);
		image_tracker[9].speed = image_tracker[9].speed*1.5; 
	}
	else if(level == 4){
		image_tracker[3].speed = 0.75*image_tracker[0].speed;
		image_tracker[4]['x'].splice(6-level,6-level);
		image_tracker[5].speed -= 1;
		
	}
}

function move(evt){
	W = canvas.width; H = canvas.height;
	switch (evt.keyCode) {
		case 38:  /* Up arrow was pressed */
			if(frog.imy == 125){
				frog.imy = 85; frog.make();
			}
			else if((frog.imy > 310)){
				frog.imy -= 30; frog.make();
			}
			else if((frog.imy > 125)){
				frog.imy -= 30; frog.make();
			}
			image_tracker[10].y = frog.imy;
			break;
		case 40:  /* Down arrow was pressed */
			if(frog.imy == 85){
				frog.imy = 125;
			}
			else if(frog.imy < 485){
				frog.imy += 30; frog.make();
			}
			image_tracker[10].y = frog.imy;
			break;
		case 37:  /* Left arrow was pressed */
			if (frog.imx - 30 > 0){
				frog.imx -= 30; frog.make();
				image_tracker[10].x = [frog.imx];
			}
			break;
		case 39:  /* Right arrow was pressed */
			if (frog.imx + 30 < W){
				frog.imx += 30; frog.make();
				image_tracker[10].x = [frog.imx];
			}
			break;
	}
	for(t = 5; t < image_tracker.length-1; t++){
		for(i = 0; i < image_tracker[t].x.length; i++){
			collision_detection(image_tracker[t]['x'][i], image_tracker[t].image.sx, t);
			
		}
	}
}

function start_game(){
      canvas = document.getElementById('game');
	  //check if canvas is supported on browser
	  if (canvas.getContext) {
		//INITIALIZE
		ctx = canvas.getContext('2d');
		W = canvas.width; H = canvas.height;
		lives = 3; score = 0; level = 0;
		
		//begin game
		biglog 	  = new imageObj(5,165,180,30);	
		racer 	  = new imageObj(45,265,30,25);
		yellowcar = new imageObj(82,265,22,25);
		medlog 	  = new imageObj(5,198,120,30); 
		shortlog  = new imageObj(5,230,100,30); 
		truck 	  = new imageObj(100,300,60,20); 
		pinkcar   = new imageObj(10,267,27,20);
		tractor   = new imageObj(72,301,27,22);
		frog 	  = new imageObj(13, 369, 22, 17); 
		deadfrog  = new imageObj(0,0,50,20);

		level_init();
		window.addEventListener('keydown',move,true);

	  }
	  else {
	    alert('Sorry, canvas is not supported on your browser!');
	  }
};