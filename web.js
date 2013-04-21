// Express initialization
var express = require('express');
var app = express(express.logger());
app.use(express.bodyParser());	//anything sent will be converted from string to json
app.use(express.methodOverride());
app.set('title', 'nodeapp');

// Mongo initialization
var mongoUri = process.env.MONGOLAB_URI || process.env.MONGOHQ_URL || 'mongodb://localhost/scorecenter';
var mongo = require('mongodb');
var db = mongo.Db.connect(mongoUri, function (error, databaseConnection) {
	db = databaseConnection;
});

//Configure environment settings related to views
app.set('views', __dirname + '/views');
app.set('view engine', 'jade');
app.use(express.logger('dev'));

//Enable CORS
app.all('/', function(req, res, next) {
	res.header("Access-Control-Allow-Origin", "*");
	res.header("Access-Control-Allow-Headers", "X-Requested-With");
	next();
});

app.use(express.static(__dirname + '/public'));

//return home page displaying list of all the scores for all games
app.get('/', function (request, response) {
	response.set('Content-Type', 'text/JSON');
	db.collection('highscores', function(er, collection) {
		collection.find().toArray(function(err, docs) {
		  	response.send(docs);
        });
    });
});


//Requests results for a username. Connects to usersearch.jade.
app.get('/usersearch', function(req, res){
	res.render('usersearch', { title: 'User Search'});
	var result = req.body.search;
	if(result){
		res.send({redirect: '/usersearch/'+result});
	}
});

//Submits results for a username. Connects to usersearch.jade
app.post('/usersearch', function (req, res) {
	var user = req.body.search;
	res.redirect('usersearch/'+user);
});

app.get('/usersearch/:id',function (req, res) {
	res.set('Content-Type', 'text/JSON');
	db.collection('highscores', function(er, collection) {
		collection.find({"username" : req.params.id }).toArray(function(err, docs) {
			res.send(docs);
		});
	});
});

//Returns the top 10 scores in descending order
//and as a JSON string (array of objects) for a specified game.
//The mandatory parameter for this API is game_title
app.get('/highscores.json', function (req, res) {
	if(req.query.game_title){
		db.collection('highscores', function(er, collection) {
			//find specified game based on query result	//descending sort based on score //top 10  //return as array of documents
			collection.find({"game_title" : req.query.game_title}).sort({"score" : -1}).limit(10).toArray(function(err, docs) {
		  		res.send(docs); //will send the array of documents after successful execution of toArray method
          });
        });		
	}
	else {
		res.send(403, 'Invalid Query')
	}		
}


//A POST API - Allows any HTML5 game on any web domain
//to send high scores to your web application.
//The mandatory fields and exact field names for this API are
//game_title, username, and score. 
app.post('/submit.json', function(req, res){
	var toInsert = {"game_title" : req.query.game_title,
					"score" : req.query.score, 
					"username" : req.query.username};
	db.collection('highscores', function(er, collection){
		collection.insert(toInsert, function(err, saved){
			if(err || !saved){
				res.send(500, "oops! highscore not saved.");
			} else {
				res.send(200, "highscore saved");
			}
			
		});	
	});
});



app.listen(process.env.PORT || 3000);