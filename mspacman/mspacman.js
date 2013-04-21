function draw(){
      canvas = document.getElementById('myCanvas');
	  
	  //check if canvas is supported on browser
	  if (canvas.getContext) {
		  context = canvas.getContext('2d');
		  context.canvas.height = window.innerHeight;
		  context.canvas.width = window.innerWidth;
		  //"by default, images are layered on the canvas in drawing
		  //order with new images layered on top of older images"
		  
		  gameboard = new Image();
		  gameboard.onload = function() {
			srcX = 315;
			srcY = 0;
			srcW = 471;
			srcH = 138;
			destW = srcW;
			destH = srcH;
			destX = 0;
			destY = 0;
			context.drawImage(gameboard, srcX, srcY, srcW, srcH, destX, destY, destW, destH);
		  };
		  gameboard.src = 'pacman10-hp-sprite.png';
		  
		  mspacman = new Image();
		  mspacman.onload = function() {
			srcX = 50;
			srcY = 20;
			srcW = 50;
			srcH = 20;
			destW = srcW;
			destH = srcH;
			destX = 155;
			destY = 29;
			context.drawImage(mspacman, srcX, srcY, srcW, srcH, destX, destY, destW, destH);
		  };
		  mspacman.src = 'pacman10-hp-sprite.png';
		  
		  ghost = new Image();
		  ghost.onload = function() {
			srcX = 120;
			srcY = 100;
			srcW = 20;
			srcH = 20;
			destW = srcW;
			destH = srcH;
			destX = 230;
			destY = 29;
			context.drawImage(ghost, srcX, srcY, srcW, srcH, destX, destY, destW, destH);
		  };	  
		  ghost.src = 'pacman10-hp-sprite.png';
	  }
	  else {
	    alert('Sorry, canvas is not supported on your browser!');
		}
}