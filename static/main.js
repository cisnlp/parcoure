$(function() {
  console.log('jquery is working!');
  // createGraph(10.0);
});




function process_sentence(sentence, languageindex) {
	var sentence_len = 0;
	var nodes = [];
	for (i = 0; i < sentence.length; i++) {
		var word = sentence[i];
		var len = word.length;
		nodes.push({start: sentence_len, len: len + 1, languageindex: languageindex, word: word});
		sentence_len += len + 1;
	};
	return [nodes, sentence_len];
};


function preprocess(input) {
	var result = {};
	var sentence_lens = {e: 0, f: 0};
	re = process_sentence(input.e, 0);
	result.nodes_e = re[0];
	rf = process_sentence(input.f, 1);
	result.nodes_f = rf[0];
	result.max_chars = Math.max(re[1], rf[1]);
	result.links = [];
	for (i = 0; i < input.alignment.length; i++) {
		result.links.push({source: input.alignment[i][0], target: input.alignment[i][1]});
	};
	return result;
};


function addpositionssub(nodes, xperchar, dx) {
	for (i = 0; i < nodes.length; i++) {
		nodes[i].xstart = dx + nodes[i].start * xperchar;
		nodes[i].xend = nodes[i].xstart + nodes[i].len * xperchar;
	};
};


function addpositions(data, xperchar, dx) {
	addpositionssub(data.nodes_e, xperchar, dx);
	addpositionssub(data.nodes_f, xperchar, dx);
};


function drawnodes(svg, nodes, y, fontsize) {
	var nodes = svg.selectAll("node")
   .data(nodes)
   .enter()
   .append("text")
   .attr("x", function(d) {
     return d.xstart
   })
   .attr("y", function(d) {
     return y
   })
   .text(function(d){return d.word})
   .attr("fill", "black")
   .attr("font-size", fontsize);
};


function drawlinks(svg, data, yl1, yl2, ypadtop, ypadbottom) {
	var links = svg.selectAll("link")
	   .data(data.links)
	   .enter()
	   .append("line")
	   .attr("class", "link")
	   .attr("x1", function(l) {
	     var sourceNode = data.nodes_e.filter(function(d, i) {
	       return i == l.source
	     })[0];
	     d3.select(this).attr("y1", yl1 + ypadtop);
	     return 0.75 * sourceNode.xstart + 0.25 * sourceNode.xend
	   })
	   .attr("x2", function(l) {
	     var targetNode = data.nodes_f.filter(function(d, i) {
	       return i == l.target
	     })[0];
	     d3.select(this).attr("y2", yl2 - ypadbottom);
	     return 0.75 * targetNode.xstart + 0.25 * targetNode.xend
	   })
	   .attr("fill", "none")
	   .attr("stroke", "grey");
};


function drawit(input) {
	data = preprocess(input)
	// SVG Container
	var svg = d3.select("#alignment")
   .append("div")
   // Container class to make it responsive.
   .classed("svg-container", true) 
   .attr("id", "my-svg-container") 
   .append("svg")
   // Responsive SVG needs these 2 attributes and no width and height attr.
   .attr("preserveAspectRatio", "xMinYMin meet")
   .attr("viewBox", "0 0 600 200")
   // Class to make it responsive.
   .classed("svg-content-responsive", true);
   // // Fill with a rectangle for visualization.
   // .append("rect")
   // .classed("rect", true)
   // .attr("width", 300)
   // .attr("height", 100);

   // Get current width and compute size numbers.
	var currentWidth = document.getElementById("my-svg-container").clientWidth;

	var spaceperchar = currentWidth / data.max_chars;
	var xperchar = Math.min(spaceperchar, 10);
	var fontsize = 12 + 12 / 30 * (xperchar - 10);
	var xrequired = xperchar * data.max_chars;
	console.log(currentWidth);
	console.log(xrequired);
	// should actually divide by 2!
	var dx = (currentWidth - xrequired) / 4;
	var yl1 = 10;
	var yl2 = 50;
	var ypad = 5;
	var fontpad = 8 + (fontsize - 12) * 0.5;

	addpositions(data, xperchar, dx)
	console.log(data)
	// var text = svg.append("text").attr("x", 50).attr("y", 50).text("TESTING").attr("fill", "red");
 	drawnodes(svg, data.nodes_e, yl1, fontsize);
 	drawnodes(svg, data.nodes_f, yl2, fontsize);
	drawlinks(svg, data, yl1, yl2, ypad, fontpad + ypad);
};


function main() {
	input = {"e": ["Das", "ist", "ein", "Beispiel", "."], 
			 "f": ["WWW", "is", "an", "example", "."], 
			 "alignment": [[0,1], [1,1], [3,2]]}
	drawit(input)
};


// main()


function createGraph(HereData) {
	drawit(HereData)
  // d3.json("/login", function(error, quotes) {// });

 //  	console.log("FINISHED");
 //  	json = JSON.parse( HereData );
 // //  	d3.json(HereData, function() {
 // //  	console.log(HereData)
	// // });
	// console.log(json)
	// console.log("HELO")
	// var svg = d3.select("#chart").append("svg")
 //                                    .attr("width", 200)
 //                                     .attr("height", 200);
	// svg.append("circle").attr("cx", 100).attr("cy", 100).attr("r", json).style("fill", "blue");
	// console.log("FINISHED")
};


// function addCircle() {
// 	var svg = d3.select("#chart").append("svg")
//                                     .attr("width", 200)
//                                      .attr("height", 200);
// 	svg.append("circle").attr("cx", 20).attr("cy", 20).attr("r", json).style("fill", "blue");
// };



