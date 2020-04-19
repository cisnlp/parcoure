$(function() {
  console.log('jquery is working!');
  // createGraph(10.0);
});

function createGraph(HereData) {
  // d3.json("/login", function(error, quotes) {// });

  	console.log("FINISHED");
  	json = JSON.parse( HereData );
 //  	d3.json(HereData, function() {
 //  	console.log(HereData)
	// });
	console.log(json)
	console.log("HELO")
	var svg = d3.select("#chart").append("svg")
                                    .attr("width", 200)
                                     .attr("height", 200);
	svg.append("circle").attr("cx", 100).attr("cy", 100).attr("r", json).style("fill", "blue");
	console.log("FINISHED")
};


// function addCircle() {
// 	var svg = d3.select("#chart").append("svg")
//                                     .attr("width", 200)
//                                      .attr("height", 200);
// 	svg.append("circle").attr("cx", 20).attr("cy", 20).attr("r", json).style("fill", "blue");
// };