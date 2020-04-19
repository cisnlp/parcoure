

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


function drawnodes(svg, nodes, y) {
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
   .attr("fill", "black");
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
	   .attr("stroke", "black");
};


function drawit(data) {

	// SVG Container
	var svg = d3.select("#container")
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
	var xperchar = 8;
	var dx = 30;
	addpositions(data, xperchar, dx)
	console.log(data)
	// var text = svg.append("text").attr("x", 50).attr("y", 50).text("TESTING").attr("fill", "red");
 	drawnodes(svg, data.nodes_e, 10);
 	drawnodes(svg, data.nodes_f, 50);
	drawlinks(svg, data, 10, 50, 5, 10 + 5);
};


function main() {
	input = {"e": ["Das", "ist", "ein", "Beispiel", "."], 
			 "f": ["That", "is", "an", "example", "."], 
			 "alignment": [[0,1], [1,1], [3,2]]}
	result = preprocess(input)
	drawit(result)
	console.log(result)
};


main()

