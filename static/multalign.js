export default function define(runtime, observer) {

  const main = runtime.module();
  const fileAttachments = new Map([["miserables.json",new URL("./files/alignments",import.meta.url)]]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));

  main.variable(observer("chart")).define("chart", ["d3","DOM","width","height","graph","margin","x","y","color","arc","step","invalidation", "clusterView"], function(d3,DOM,width,height,graph,margin,x,y,color,arc,step,invalidation, clusterView)
{

  var svgcont = d3.select("#my-svg-content-responsive")   
  .append("div")
  // Container class to make it responsive.
  .classed("svg-container", true) 
  .attr("id", "my-svg-container");
  // SVG Container
  var svg2 = svgcont.append("svg")
  .attr("id", "my-svg-content-responsive");
  var maxWidth = 0;
  var totalWidth = margin.left;
  var prevHalfWidth = 0;
  svg2.append('g')
        .selectAll('.dummyText')
        .data(graph.nodes)
        .enter()
        .append("text")
        .attr("fill", "black")
        .attr("font-family", "sans-serif")
        .attr("font-size", 20)
        .text(function(d) { return d.tag})
        .each(function(d,i) {
            var thisWidth = this.getComputedTextLength();
            if (d.pos == 1) {
              totalWidth = margin.left;
            }
            totalWidth = totalWidth + prevHalfWidth + thisWidth/2 +10;
            d.x = totalWidth
            prevHalfWidth = thisWidth/2
            if(totalWidth>maxWidth) maxWidth = totalWidth;
            this.remove() // remove them just after displaying them
        });
  

  const svg = d3.select(DOM.svg(maxWidth+50, height)).attr("class", "bold");

  svg.append("style").text(`

.hover path {
  stroke: #ccc;
}

.hover text {
  fill: #ccc;
}

.hover g.primary text {
  fill: black;
  font-weight: bold;
}

.hover g.secondary text {
  fill: #333;
}

.hover path.primary {
  stroke: #333;
  stroke-opacity: 1;
}

.bold path {
  stroke: #ccc;
}

.bold text {
  fill: #ccc;
}

.bold g.preset_primary text {
  fill: black;
  font-weight: bold;
}

.bold g.preset_secondary text {
  fill: #333;
}

.bold path.preset_primary {
  stroke: #333;
  stroke-opacity: 1;
}
`);


      
  // insert dots and text for nodes
  const label = svg.append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 20)
    .selectAll("g")
    .data(graph.nodes)
    .join("g")
      .attr("transform", d => `translate(${d.x = d.x},${d.y = y(d.group)})`)
      .classed("preset_primary", d=> d.bold)
      .classed("preset_secondary", d=> d.sbold)
      .call(g => g.append("text")
          .attr("y", -16)
          .attr("fill", d => d3.lab(color(d.group)).darker(2))
          .text(d => d.tag)
          )
          .style("text-anchor", "middle")
      .call(g => g.append("circle")
          .attr("r", 9)
          .attr("fill", d => color(d.group)))
      

  // inserting links
  const path = svg.insert("g", "*")
      .attr("fill", "none")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1.5)
    .selectAll("path")
    .data(graph.links)
    .join("path")
      .attr("stroke", d => d.source.group === d.target.group ? color(d.source.group) : "#aaa")
      .attr("d", arc)
      .classed("preset_primary", d => d.source.bold || d.target.bold || ((d.source.sbold || d.target.sbold) && clusterView) );

  const overlay = svg.append("g")
      .attr("fill", "none")
      .attr("pointer-events", "all")
    .selectAll("rect")
    .data(graph.nodes)
    .join("rect")
      .attr("width", margin.left + 40)
      .attr("height", step)
      .attr("y", d => y(d.group) - step / 2)
      .attr("x", d => d.x - 5)
      .on("mouseover", d => {
        svg.classed("hover", true);
        svg.style("cursor", "pointer");
        label.classed("primary", n => n == d );
        label.classed("secondary", n => n.sourceLinks.some(l => l.target === d) || n.targetLinks.some(l => l.source === d));
        path.classed("primary", l => l.source === d || l.target === d || (d.connectedNodes.some(p => l.source === p) && clusterView) || (d.connectedNodes.some(p => l.target === p) && clusterView));
      })
      .on("mouseout", d => {
        svg.classed("hover", false);
        svg.style("cursor", "");
        label.classed("primary", false);
        label.classed("secondary", false);
        path.classed("primary", false).order();
      })
      .on("click", d => {
        console.log(d.tag);
        if (d.target_languages.length > 0) {
          var newForm = jQuery('<form>', {
              'action': '/lexicon',
              'method': 'post',
          })
          .append(jQuery('<input>', {
              'name': 'source_language',
              'value': d.source_language
          }))
          .append(jQuery('<input>', {
              'name': 'query',
              'value': d.tag
          }));

          for(let i = 0; i< d.target_languages.length; i++){
              newForm.append(jQuery('<input>', {
                  'name': "target_languages",
                  'value': d.target_languages[i]
              }))
          }
          
          newForm.appendTo('body').submit();
        }
    });

 
  return svg.node();
}
);
  main.variable(observer("arc")).define("arc", ["margin", "step"], function(margin, step){return(
function arc(d) {
  const y1 = d.source.y;
  const y2 = d.target.y;
  const x1 = d.source.x;
  const x2 = d.target.x;
  const midx = (x1  );
  const midy = (y1);
  const midx2 = x2 ;
  const midy2 = y2;
  return `M ${x1} ${y1} C ${midx} ${midy} ${midx2} ${midy2} ${x2} ${y2}`;
}
)});
  main.variable(observer("y")).define("y", ["d3","graph","margin","height"], function(d3,graph,margin,height){return(
d3.scalePoint(graph.nodes.map(d => d.group), [margin.top, height - margin.bottom])
)});
  main.variable(observer("x")).define("x", ["d3","graph","margin","width"], function(d3,graph,margin,width){return(
d3.scalePoint(graph.nodes.map(d => d.pos), [ margin.left, width - margin.right])
)});
  main.variable(observer("margin")).define("margin", function(){return(
{top: 50, right: 100, bottom: 20, left: 50}
)});
  main.variable(observer("height")).define("height", ["data","step","margin"], function(data,step,margin){return(
(data.groups) * step + margin.top + margin.bottom
)});
  main.variable(observer("width")).define("width", ["data","step","margin"], function(data,step,margin){return(
(data.poses) * step + margin.left + margin.right
)});
  main.variable(observer("step")).define("step", function(){return(
64
)});
  main.variable(observer("color")).define("color", ["d3","graph"], function(d3,graph){return(
d3.scaleOrdinal(graph.nodes.map(d => d.group).sort(d3.ascending), d3.schemeCategory10)
)});
  main.variable(observer("graph")).define("graph", ["data"], function(data)
{
  const nodes = data.nodes.map(({id, tag, group, pos, bold, source_language, target_langs}) => ({
    id,
    tag,
    sourceLinks: [],
    targetLinks: [],
    connectedNodes: [],
    group,
    pos, 
    bold,
    sbold: false,
    source_language,
    target_languages: target_langs
  }));

  const nodeById = new Map(nodes.map(d => [d.id, d]));

  const links = data.links.map(({source, target, bold}) => ({
    source: nodeById.get(source),
    target: nodeById.get(target),
    bold
  }));

  for (const link of links) {
    const {source, target, bold} = link;
    source.sourceLinks.push(link);
    target.targetLinks.push(link);
    source.connectedNodes.push(target);
    target.connectedNodes.push(source);
    if (source.bold || target.bold){
      if (source.bold){
        target.sbold = true;
      } else {
        source.sbold = true;
      }

    }

  }

  return {nodes, links};
}
);
  main.variable(observer("data")).define("data", ["FileAttachment"], function(FileAttachment){return(
FileAttachment("miserables.json").json()
)});
   main.variable(observer("clusterView")).define("clusterView", [], function(ldata){return(
   false
)});

  main.variable(observer("d3")).define("d3", ["require"], function(require){return(
require("d3@5")
)});
  return main;
}
