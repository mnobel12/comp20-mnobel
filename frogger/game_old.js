var ctx; var canvas;
var frog_x; var frog_y;
var lives; var level; var score;
highscore = 0; //will have to account for this

/////SPRITES/////
roadside = new Image(); roadside.src = 'assets/frogger_sprites.png';
header = new Image(); header.src = 'assets/frogger_sprites.png';
lifesprite = new Image(); lifesprite.src = 'assets/frogger_sprites.png';
bigLog = new Image(); bigLog.src = 'assets/frogger_sprites.png';
vehicle1 = new Image(); vehicle1.src = 'assets/frogger_sprites.png';
vehicle2 = new Image(); vehicle2.src = 'assets/frogger_sprites.png';
    //frog
frogU = new Image(); frogU.src = 'assets/frogger_sprites.png'; //up

//**NOTE: EVENTUALLY WILL PUT THE ABOVE INTO AN IMAGE LOADER FUNCTION **//
//**AND CREATE ARRAYS FOR CERTAIN IMAGE ELEMENTS **//


//function for drawing roadsides
function roadsides(posY){
	W = canvas.width; H_roadsides = 40;
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
	//draw image
	ctx.drawImage(roadside, 0, 115,W, H_roadsides, 0,posY,W,H_roadsides);
};

function store_image_data(){};
function initial_image_data(){
	frog_x = 200; frog_y = 480; //frog_y is based on location & width of lower roadside

	//DRAW EXTRA STUFF FOR A2
	//later I will put things like vehicles and logs into arrays that I will animate
	ctx.drawImage(frogU,12,360,30,30,frog_x,frog_y,35,35);
	ctx.drawImage(bigLog,5,165,180,30,160,140,180,30);
	ctx.drawImage(vehicle1,45,265,30,35,30,320,30,30);
	ctx.drawImage(vehicle2,77,265,30,35,80,360,30,30);
};

function level_update(newLevel){
	W = canvas.width; H = canvas.height;

	ctx.clearRect(0,0,W,H); //reset canvas
	
	//-------------------------
	//DRAW THE BACKGROUND IMAGE
	//-------------------------
	//WATER
	H_water = 290;
	ctx.fillStyle = "#191970";
	ctx.fillRect(0,0,W, H_water);
	
	//HEADER
	H_header = 110;
	ctx.drawImage(header, 0, 0,W, H_header, 0, 0,W,H_header);
	
	//ROAD
	H_road = H - H_water;
	ctx.fillStyle = "#000000";
	ctx.fillRect(0,290,W, H_road);
	
	//ROADSIDES
	roadsides(265);
	roadsides(480);

	//------------------------------------------
	//DRAW ELEMENTS BASED ON VARIABLE PARAMETERS
	//------------------------------------------
	if(newLevel == 1){
		level += 1;
		initial_image_data();
	} //else {
		//RESTORE ALL VARIABLE IMAGE DATA like positions of cars and logs etc
	//}
	
	//FOOTER
	footer = 520; 
	//lives
	for (i = 0; i < lives; i += 1) {
		ctx.drawImage(lifesprite,12,330,30,30,i*20,footer,20,20);
	}
	//level
	ctx.fillStyle    = '#00FF00';
    ctx.font         = 'Bold 20px Sans-Serif';
    ctx.textBaseline = 'top';
    ctx.fillText  ('Level '+level, 70, footer);
	//score & highscore
	ctx.font = 'Bold 15px Sans-Serif';
	ctx.fillText  ('Score: '+score,0,footer+20); 
	ctx.fillText  ('Highscore: '+highscore,150,footer+20);
	
};

function start_game(){
      canvas = document.getElementById('game');
	  //check if canvas is supported on browser
	  if (canvas.getContext) {
		//INITIALIZE
		ctx = canvas.getContext('2d');
		lives = 3; score = 0; level = 0;
		//begin game
		level_update(1);
	  }
	  else {
	    alert('Sorry, canvas is not supported on your browser!');
	  }
};