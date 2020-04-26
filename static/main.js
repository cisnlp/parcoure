// $(function() {
//   console.log('jquery is working!');
// });


// var BrowserText = (function () {
//     var canvas = document.createElement('canvas'),
//         context = canvas.getContext('2d');

//     *
//      * Measures the rendered width of arbitrary text given the font size and font face
//      * @param {string} text The text to measure
//      * @param {number} fontSize The font size in pixels
//      * @param {string} fontFace The font face ("Arial", "Helvetica", etc.)
//      * @returns {number} The width of the text
//      *
//     function getWidth(text, fontSize, fontFace) {
//         context.font = fontSize + 'px ' + fontFace;
//         return context.measureText(text).width;
//     }

//     return {
//         getWidth: getWidth
//     };
// })();


// function get_max_length_depr(data, fontsize, font) {
// 	le = BrowserText.getWidth(data.e.join(" "), fontsize, font)
// 	lf = BrowserText.getWidth(data.f.join(" "), fontsize, font)
// 	return Math.max(le, lf)
// };


function process_sentence(sentence, languageindex, lengths, spacewidth) {
	var sentence_len = 0;
	var current_x = 0;
	var nodes = [];
	for (i = 0; i < sentence.length; i++) {
		var word = sentence[i];
		var len = word.length;
		var x = lengths[i];
		nodes.push({start: sentence_len, 
					len: len + 1, 
					languageindex: languageindex, 
					word: word, 
					xstart: current_x,
					xend: current_x + x});
		sentence_len += len + 1;
		current_x += x + spacewidth;
	};
	return [nodes, sentence_len];
};


function preprocess(input, lengths, spacewidth) {
	var result = {};
	var sentence_lens = {e: 0, f: 0};
	re = process_sentence(input.e, 0, lengths.e, spacewidth);
	result.nodes_e = re[0];
	rf = process_sentence(input.f, 1, lengths.f, spacewidth);
	result.nodes_f = rf[0];
	result.max_chars = Math.max(re[1], rf[1]);
	result.links = [];
	for (i = 0; i < input.alignment.length; i++) {
		result.links.push({source: input.alignment[i][0], target: input.alignment[i][1]});
	};
	return result;
};



function drawnodes(svg, nodes, y, fontsize, dx) {
	var nodes = svg.selectAll("node")
   .data(nodes)
   .enter()
   .append("text")
   .attr("x", function(d) {
     return d.xstart + dx
   })
   .attr("y", function(d) {
     return y
   })
   .text(function(d){return d.word})
   .attr("fill", "black")
   .attr("font-size", fontsize);
};


function drawlinks(svg, data, yl1, yl2, ypadtop, ypadbottom, dx, stroke) {
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
	     return 0.5 * sourceNode.xstart + 0.5 * sourceNode.xend + dx
	   })
	   .attr("x2", function(l) {
	     var targetNode = data.nodes_f.filter(function(d, i) {
	       return i == l.target
	     })[0];
	     d3.select(this).attr("y2", yl2 - ypadbottom);
	     return 0.5 * targetNode.xstart + 0.5 * targetNode.xend + dx
	   })
	   .attr("fill", "none")
	   .attr("stroke", "#00A30B")
	   .attr("stroke-width", stroke);
};


function get_lengths(svg, data, fontsize) {
	widths = [];
	svg.append('g')
	    .selectAll('.dummyText')
	    .data(data)
	    .enter()
	    .append("text")
	    .attr("fill", "black")
	    .attr("font-size", fontsize)
	    .text(function(d) { return d})
	    .each(function(d,i) {
	        var thisWidth = this.getComputedTextLength()
	        widths.push(thisWidth)
	        this.remove() // remove them just after displaying them
	    });
	return widths
};

function get_sentence_length(lengths, spacewidth) {
	return lengths.reduce((a, b) => a + b, 0) + lengths.length * spacewidth
};



function compute_lengths(svg, input, basefontsize, spacewidth) {
   var lengths = {};
   lengths.e = get_lengths(svg, input.e, basefontsize);
   lengths.f = get_lengths(svg, input.f, basefontsize);
   lengths.etotal = get_sentence_length(lengths.e, spacewidth)
   lengths.ftotal = get_sentence_length(lengths.f, spacewidth)
   lengths.maxreq = Math.max(lengths.etotal, lengths.ftotal)
   return lengths
};

function drawit(input, offset) {
	// some measures
	var basefontsize = 12;
	var spacewidth = 5;
	var currentWidth = 600;
	var fontpad = 8;
	var ypad = 5;
	var stroke = 1.5;

	if (!!document.getElementById("my-svg-container")) {
		console.log("using existing")
		var svgcont = d3.select("#my-svg-container")
	} else {
		console.log("creating")
			var svgcont = d3.select("#alignment")
   .append("div")
   // Container class to make it responsive.
   .classed("svg-container", true) 
   .attr("id", "my-svg-container");
	}

	// SVG Container
	var svg = svgcont.append("svg")
   // Responsive SVG needs these 2 attributes and no width and height attr.
   .attr("preserveAspectRatio", "xMinYMin meet")
   .attr("viewBox", "0 " + offset * 75 + " 600 " + (offset + 1) * 75)
   // Class to make it responsive.
   .classed("svg-content-responsive", true);
   // // Fill with a rectangle for visualization.
   // .append("rect")
   // .classed("rect", true)
   // .attr("width", 300)
   // .attr("height", 100);

   var lengths = compute_lengths(svg, input, basefontsize, spacewidth)

   if (lengths.maxreq > currentWidth) {
   		console.log("ADJUSTING SIZES")
   		//reduce font size
   		console.log((1 - lengths.maxreq / (currentWidth * 25) ))
   		scalefactor = currentWidth / lengths.maxreq * (1 - lengths.maxreq / (currentWidth * 25) )
   		spacewidth *= scalefactor;
   		basefontsize *= scalefactor
   		fontpad *= scalefactor
   		ypad *= scalefactor
   		stroke *= scalefactor
	    var lengths = compute_lengths(svg, input, basefontsize, spacewidth)
	    console.log(lengths.maxreq)
   };

	data = preprocess(input, lengths, spacewidth);

	var dx = (currentWidth - lengths.maxreq) / 2;
	var yl1 = 15;
	var yl2 = 65;

 	drawnodes(svg, data.nodes_e, yl1, basefontsize, dx);
 	drawnodes(svg, data.nodes_f, yl2, basefontsize, dx);
	drawlinks(svg, data, yl1, yl2, ypad, fontpad + ypad, dx, stroke);
};


function main() {
	input = {"e": ["Das", "ist", "ein", "Beispiel", "."], 
			 "f": ["WWW", "is", "an", "example", "."], 
			 "alignment": [[0,1], [1,1], [3,2]]}
	// input = {"e": ['Das', 'ist', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', ',', 
	// 'Das', 'ist', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', '!', 
	// 'Das', 'ist', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', '!', 
	// 'Das', 'ist', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', '!', ], 
	// 		 "f": ['Das', 'ist', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', ',', 'ein', 'extrem', 'langer', 'Satz', ','], 
	// 		 "alignment": [[0,1], [1,1], [3,2]]}

	drawit(input)
};


main()


function createGraph(HereData, offset) {
	drawit(HereData, offset)
};





