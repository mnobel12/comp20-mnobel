var myLat = 0;
var myLng = 0;
var me = new google.maps.LatLng(myLat, myLng);
var myOptions = {
			zoom: 11, 
			center: me,
			mapTypeId: google.maps.MapTypeId.ROADMAP
		};
var map;
var marker;
var infowindow = new google.maps.InfoWindow();


function init()
{
	map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	getMyLocation();
}

function getMyLocation()
{
	if (navigator.geolocation) { // the navigator.geolocation object is supported on your browser
		navigator.geolocation.getCurrentPosition(function(position) {
			myLat = position.coords.latitude;
			myLng = position.coords.longitude;
			renderMap();
			plotRedLine();
			findFriends();

		});
	}
	else {
		alert("Geolocation is not supported by your web browser.  What a shame!");
	}
}

function renderMap()
{
	me = new google.maps.LatLng(myLat, myLng);
	
	// Update map and go there...
	map.panTo(me);

	// Create a marker
	marker = new google.maps.Marker({
		position: me,
		title: "I am here at... ("+myLat+", "+myLng+")"
	});
	marker.setMap(map);
	infowindow.setContent(marker.title);
	infowindow.open(map, marker);
}

function plotRedLine()
{	
	//plot red line data
	arrival_times = schedule();
	redLine = redLineData(arrival_times);
	redLinePath = []; min_distance = [-1,100000];
	for (var key in redLine) {
		redLinePath[key] = createRedLineMarker(redLine[key],'',redLine[key][2]);
		dist = findDistance(myLat,myLng,redLine[key][1][0],redLine[key][1][1]);
		if(dist < min_distance[1]){ 
			min_distance[0] = key;
			min_distance[1] = dist; 
		}
	}
	min_loc = min_distance[0];
	createRedLineMarker(redLine[min_loc],min_distance[1],redLine[min_loc][2]);
	
	polyPath = new google.maps.Polyline({
		path: redLinePath,
		strokeColor: "#FF0000",
		strokeOpacity: 1.0,
		strokeWeight: 4
	});
	polyPath.setMap(map);
}

//translate CSV to json-type string
function parseCSV(s) {
	var arr = '[', fields = [];
	var c = col = 0;
	for (c; c < s.length; c++) {
		var cc = s[c], nc = s[c+1];
		fields[col] = fields[col] || '';
		if (cc == ',') { ++col; continue; }
		if (cc == '\n') { break; }
		if (cc != '\r') { fields[col] += cc; }
	}	
	var rail_line = ''; col = 0; c = c-1;
	for (c; c < s.length; c++) {
		var cc = s[c], nc = s[c+1];
		rail_line = rail_line || ('{"'+fields[col]+'":"');			
		if (cc == ',') {
			col++;
			rail_line += '","'+fields[col]+'":"'; //add new dictionary entry
			continue; 
		}
		if (cc == '\n') {
			if(col > 0){
				arr += rail_line + '"}';
				if(c < s.length-2){ arr += ','; }
			}
			rail_line = ''; col = 0;
			continue;
		}
		if (cc != '\r') { 
			rail_line	+= cc; 
		}
	}
	arr += ']';
	return arr;
}

function schedule(){
	str = makeHTTPrequest();
	if (str == null) {
	  alert("Error creating request object --Ajax not supported?");
	}
	else {
		arrivals = {}; mapper_str = '';
		str.onreadystatechange = function parse() {
			//get json string from website, get relevant data, group by station, and return
			if((str.readyState == 4) && (str.status == 200)){
				mapper_str = JSON.parse(str.responseText);
			}
		};
		str.open("GET", "http://mbtamap.herokuapp.com/mapper/redline.json",false);
		str.send('');
		if(mapper_str != ''){
			for(i=0; i < mapper_str.length; i++){
				key = mapper_str[i]['PlatformKey'];
				dir = '';
				if(key[key.length-1] == 'N'){ dir = 'NORTH-BOUND'; }
				else{ 
					dir = 'SOUTH-BOUND'; 
				}
				if(arrivals[key] == undefined){ 
					arrivals[key] = [];	
				}
				newTime = mapper_str[i]['Time'].split(" ");
				arrivals[key].push(['<br>'+newTime[1]+' '+newTime[2]+' '+dir]);
			}
		}			
		return arrivals;
	}
}

function redLineData(arrivals)
{
	str = makeHTTPrequest();
	redLine = {};
	if (str == null) {
	  alert("Error creating request object --Ajax not supported?");
	}
	else {
		str.onreadystatechange = function(){
			if((str.readyState == 4)){ 
				//parse CSV
				var raildata = JSON.parse(parseCSV(str.responseText));
				for(i = 0; i < raildata.length; i++){
					if (raildata[i]['Line'] != "Red"){ break; }
					stationName = raildata[i]['StationName']
					if(redLine[stationName] == undefined){
						redLine[stationName] = [stationName, [parseFloat(raildata[i]['stop_lat']),
					               				      parseFloat(raildata[i]['stop_lon'])], 
					              			arrivals[raildata[i]['PlatformKey']]];
					}
					else {
						if(redLine[stationName][2] == undefined){ redLine[stationName][2] = []; }
						(redLine[stationName][2]).push.apply(redLine[stationName][2], 
										     arrivals[raildata[i]['PlatformKey']]);
					}
					if(redLine[stationName][2] != undefined){ (redLine[stationName][2]).sort() };
				}
			}
		}
		str.open("GET", "./RealTimeHeavyRailKeys.csv",false);
		str.send('');
	}
	return redLine;
}
			
function createRedLineMarker(place,min,myarrivals)
{
	place_loc = new google.maps.LatLng(place[1][0],place[1][1]);
	place_desc= place[0]+" T station"
	if( min != ''){
		place_desc = "*closest station to current location*<br>"+place_desc+"<br>distance = "+min.toFixed(3)+" miles"
	}
	if((myarrivals != undefined) && (myarrivals.length > 0)){
		for(at = 0; at < myarrivals.length; at++){
			place_desc += myarrivals[at];
		}
	}
	var marker = new google.maps.Marker({
		position: place_loc,
		title: place_desc,
		icon: 'redLineSym.png'
	});
	marker.setMap(map);
	google.maps.event.addListener(marker, 'click', function() {
		infowindow.close();
		infowindow.setContent(marker.title);
		infowindow.open(map, marker);
	});
	return place_loc;
}

function toRad(number){
	return number*Math.PI/180;
}

function findDistance(lat1,lon1,lat2,lon2){
	R = 6371; // km 
	dLat = toRad((lat2-lat1));
	dLon = toRad((lon2-lon1));
	a = Math.sin(dLat/2)*Math.sin(dLat/2) + 
		Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*
		Math.sin(dLon/2)*Math.sin(dLon/2);
	c = 2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
	d = R*c*0.621371; //convert to miles
	return d;
}

function findFriends(){

	request = makeHTTPrequest();
	if (request == null) {
		alert("Error creating request object --Ajax not supported?");
	}
	else {
		//get carmen and waldo info and display them
		request.onreadystatechange = function friendMapper(){
			if((request.readyState == 4) && (request.status == 200)){
				friend_str = JSON.parse(request.responseText);
				for(i=0; i < friend_str.length; i++){
					//get the name
					friendname = friend_str[i]['name'];
					friendname_lower = ((friendname.split(" "))[0]).toLowerCase();
					//get the latitude and longitude
					friendLoc = friend_str[i]['loc'];
					friendLat = parseFloat(friendLoc['latitude']);
					friendLon = parseFloat(friendLoc['longitude']);
					markerLoc = new google.maps.LatLng(friendLat, friendLon);
					//create content
					markerDesc = friendname;
					if(friendLoc['note'] != undefined){
						markerDesc = friendLoc['note'];
					}
					markerDesc += ' ('+friendLat+', '+friendLon+')';					
					//get icon
					markerIcon = friendname_lower+'.png';
				
					newmarker = new google.maps.Marker({
						position: markerLoc,
						title: markerDesc,
						icon: markerIcon
					});
					newmarker.setMap(map);

					//calculate and display distance
					d = findDistance(myLat, myLng, friendLat, friendLon);
					myTextDiv = document.getElementById('friend_distances');
					myLabel = document.createElement('h1');
					myLabel.innerHTML = 'The distance to<br>'+friendname+'<br>is '+d.toFixed(3)+' miles';
					myTextDiv.appendChild(myLabel);
					map.controls[google.maps.ControlPosition.TOP_RIGHT].push(myTextDiv); 
				}
			}
		};
		request.open("GET", "http://messagehub.herokuapp.com/a3.json", true);
		request.send('');
	}
}

function makeHTTPrequest(){
	var request;
	try { 
		request = new XMLHttpRequest(); //chrome, firefox, etc
	} 
	catch (ms1) {
		try {
			request = new ActiveXObject("Msxml2.XMLHTTP"); //IE7 +
		}
		catch (ms2) {
			try {
				request = new ActiveXObject("Microsoft.XMLHTTP"); //IE5
			} 
			catch (ex) {
				request = null;
			}
		}
	}
	return request;
}
