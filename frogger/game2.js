var ctx; var canvas;
var frog_x; var frog_y;
var lives; var level; var score;
highscore = 0; //will have to account for this
image_tracker = []; //content in the form of [[image, xy coords]*number of images in track, speed] 
count = 0; loopcnt = 0;

var medlog, biglog, shortlog;
var truck, grayracer, pinkcar, yellowcar, tractor;

sprites = new Image(); sprites.src = 'assets/frogger_sprites.png';
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


function store_image_data(){};
function initial_image_data(){
	frog_x = 200; frog_y = 480; //frog_y is based on location & width of lower roadside

	//DRAW EXTRA STUFF FOR A2
	//later I will put things like vehicles and logs into arrays that I will animate
	ctx.drawImage(sprites,12,360,30,30,frog_x,frog_y,35,35); //frog facing upwards
	ctx.drawImage(sprites,5,165,180,30,160,140,180,30); 	 //big log
	ctx.drawImage(sprites,45,265,30,35,30,320,30,30); 		 //gray racer
	ctx.drawImage(sprites,77,265,30,35,80,360,30,30); 		 //vehicle 2
};

//-------------------------
//DRAW THE BACKGROUND IMAGE
//-------------------------

function roadsides(posY){
	//function for drawing roadsides
	W = canvas.width; 
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
	W = canvas.width; H = canvas.height;

	//WATER
	H_water = 290;
	ctx.fillStyle = "#191970";
	ctx.fillRect(0,0,W, H_water);
	
	//HEADER
	H_header = 110;
	ctx.drawImage(sprites, 0, 0,W, H_header, 0, 0,W,H_header);
	
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
function animate(){
	ctx.clearRect(0,0,W,H); //reset canvas	
	background();
	count++;	
	
	for(t = 0; t < image_tracker.length; t++){
		for(i = 0;  i < image_tracker[t]['x'].length; i++){
	
	
			image_tracker[t]['x'][i] += image_tracker[t].speed;
			console.log(image_tracker[t]['x'][i]);
			if (image_tracker[t]['x'][i] >= W){
				loopcnt++;
				console.log('hi!');
				image_tracker[t]['x'][i] = -image_tracker[t].image.swidth;
				//for(j = 0; j < storage.length; j++){
				//	image_tracker[0]['x'][j] = storage[j];
				//}
			} 
			image_tracker[t]['image'].imy = image_tracker[t].y;
			myx = image_tracker[t]['x'][i];
			image_tracker[t].image.imx = myx;
			//console.log(image_tracker[0].image);
			if((myx < W) && (myx >= -image_tracker[t].image.swidth)){
				//console.log(i+': '+image_tracker[0]['x'][i]+'+'+count*5+'='+myx);
				//console.log(image_tracker[0].image);
				image_tracker[t].image.make();
			}
		}
	}
}

function level_init(){
	W = canvas.width; H = canvas.height;
	level += 1;

	//set up image "tracks" (image_tracker) 
	
	//timing
	big_sp = (W - 3*medlog.swidth-30)/3; med_sp = (W - 3*medlog.swidth)/4; small_sp = (W - 2*medlog.swidth)/2;
	truck_sp = (W - 2*truck.swidth); 
	
	if(level == 1){
		image_tracker[0] = {'image': medlog, 'x': [-medlog.swidth, -(2*medlog.swidth+med_sp), -(3*medlog.swidth+3*med_sp)], 'y': 115, 'speed': 2};
		
		image_tracker[1] = {'image': biglog, 'x': [-biglog.swidth-30, -(2*biglog.swidth+30+2*big_sp), -(3*biglog.swidth+30+3*big_sp)], 'y': 175, 'speed': 3};
		
		image_tracker[2] = {'image': shortlog, 'x':  [-W, -W+(shortlog.swidth + small_sp), -W+(2*shortlog.swidth+2*small_sp)], 'y': 235, 'speed': 1};

		image_tracker[3] = {'image': truck, 'x': [-W/2-5*truck.swidth/2, -W/2+3*truck.swidth/2], 'y': 335, 'speed': 1};

		setInterval(animate,30);
	}

}


function level_update(newLevel){
	level_init();
	
};

function start_game(){
      canvas = document.getElementById('game');
	  //check if canvas is supported on browser
	  if (canvas.getContext) {
		//INITIALIZE
		ctx = canvas.getContext('2d');
		lives = 3; score = 0; level = 0;
		
		//begin game
		biglog = new imageObj(5,165,180,30);	
		grayracer = new imageObj(45,265,30,35);
		yellowcar = new imageObj(77,265,30,35);
		medlog = new imageObj(5,198,120,30); 
		shortlog = new imageObj(5,230,100,30); 
		truck = new imageObj(100,300,60,30); 
		pinkcar = new imageObj(5,265,35,35);
		tractor = new imageObj(70,300,35,30); 
		level_update(1);
		
		
	  }
	  else {
	    alert('Sorry, canvas is not supported on your browser!');
	  }
};