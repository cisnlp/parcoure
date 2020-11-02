export default function define(runtime, observer) {
  // console.log(runtime);
  // console.log(observer);
  const main = runtime.module();
  const fileAttachments = new Map([["miserables.json",new URL("./files/alignments",import.meta.url)]]);
  main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
//   main.variable(observer()).define(["md"], function(md){return(
// md`# Arc Diagram

// This diagram places nodes in a horizontal or vertical line, with circular arcs for links. Unlike other network visualizations such as a [force layout](/@d3/force-directed-graph), the appearance (and usefulness) of an arc diagram is highly dependent on the order of nodes. Hover over a node below to inspect its connections.`
// )});
// This part create a frame to choose the order in which nodes are shown, which we don't use
  main.variable(observer("viewof order")).define("viewof order", ["d3","html"], function(d3,html)
{
  const options = [
    {name: "Order by name", value: (a, b) => d3.ascending(a.id, b.id)},
    {name: "Order by group", value: (a, b) => a.group - b.group || d3.ascending(a.id, b.id)},
    {name: "Order by degree", value: (a, b) => d3.sum(b.sourceLinks, l => l.value) + d3.sum(b.targetLinks, l => l.value) - d3.sum(a.sourceLinks, l => l.value) - d3.sum(a.targetLinks, l => l.value) || d3.ascending(a.id, b.id)}
  ];
  const form = html`<form style="display: flex; align-items: center; min-height: 33px;"><select name=i>${options.map(o => Object.assign(html`<option>`, {textContent: o.name}))}`;
  const timeout = setTimeout(() => {
    form.i.selectedIndex = 1;
    form.dispatchEvent(new CustomEvent("input"));
  }, 2000);
  form.onchange = () => {
    form.dispatchEvent(new CustomEvent("input")); // Safari
  };
  form.oninput = (event) => {
    if (event.isTrusted) form.onchange = null, clearTimeout(timeout);
    form.value = options[form.i.selectedIndex].value;
  };
  form.value = options[form.i.selectedIndex].value;
  return form;
}
);
  // main.variable(observer("order")).define("order", ["Generators", "viewof order"], (G, _) => G.input(_));
  main.variable(observer("chart")).define("chart", ["d3","DOM","width","height","graph","margin","x","y","color","arc","step","viewof order","invalidation"], function(d3,DOM,width,height,graph,margin,x,y,color,arc,step,$0,invalidation)
{
  const svg = d3.select(DOM.svg(width, height));

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

`);

  // insert dots and text for nodes
  const label = svg.append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 20)
      .attr("text-anchor", "end")
    .selectAll("g")
    .data(graph.nodes)
    .join("g")
      .attr("transform", d => `translate(${d.x = x(d.pos)},${d.y = y(d.group)})`)
      .call(g => g.append("text")
          .attr("y", -16)
          // .attr("x", d => (d.pos - 1) * step /2)
          // .attr("dy", "0.35em")
          .attr("fill", d => d3.lab(color(d.group)).darker(2))
          .text(d => d.tag))
          .style("text-anchor", "middle")
      .call(g => g.append("circle")
          .attr("r", 9)
          .attr("fill", d => color(d.group)));

  // inserting links
  const path = svg.insert("g", "*")
      .attr("fill", "none")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1.5)
    .selectAll("path")
    .data(graph.links)
    .join("path")
      .attr("stroke", d => d.source.group === d.target.group ? color(d.source.group) : "#aaa")
      .attr("d", arc);

  const overlay = svg.append("g")
      .attr("fill", "none")
      .attr("pointer-events", "all")
    .selectAll("rect")
    .data(graph.nodes)
    .join("rect")
      .attr("width", margin.left + 40)
      .attr("height", step)
      .attr("y", d => y(d.group) - step / 2)
      .attr("x", d => x(d.pos) - step / 2)
      .on("mouseover", d => {
        svg.classed("hover", true);
        label.classed("primary", n => n === d);
        label.classed("secondary", n => n.sourceLinks.some(l => l.target === d) || n.targetLinks.some(l => l.source === d));
        path.classed("primary", l => l.source === d || l.target === d).filter(".primary").raise();
      })
      .on("mouseout", d => {
        svg.classed("hover", false);
        label.classed("primary", false);
        label.classed("secondary", false);
        path.classed("primary", false).order();
      });

  // function update() {
  //   y.domain(graph.nodes.sort($0.value).map(d => d.id));

  //   const t = svg.transition()
  //       .duration(750);

  //   label.transition(t)
  //       .delay((d, i) => i * 20)
  //       .attrTween("transform", d => {
  //         const i = d3.interpolateNumber(d.y, y(d.id));
  //         return t => `translate(${margin.left},${d.y = i(t)})`;
  //       });

  //   path.transition(t)
  //       .duration(750 + graph.nodes.length * 20)
  //       .attrTween("d", d => () => arc(d));

  //   overlay.transition(t)
  //       .delay((d, i) => i * 20)
  //       .attr("y", d => y(d.id) - step / 2);
  // }

  // $0.addEventListener("input", update);
  // invalidation.then(() => $0.removeEventListener("input", update));

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
  const nodes = data.nodes.map(({id, tag, group, pos}) => ({
    id,
    tag,
    sourceLinks: [],
    targetLinks: [],
    group,
    pos
  }));

  const nodeById = new Map(nodes.map(d => [d.id, d]));

  const links = data.links.map(({source, target, value}) => ({
    source: nodeById.get(source),
    target: nodeById.get(target),
    value
  }));

  for (const link of links) {
    const {source, target, value} = link;
    source.sourceLinks.push(link);
    target.targetLinks.push(link);
  }

  return {nodes, links};
}
);
  main.variable(observer("data")).define("data", ["FileAttachment"], function(FileAttachment){return(
FileAttachment("miserables.json").json()
)});
//   main.variable(observer("data")).define("data", ["ldata"], function(ldata){return(
// data
// )});

  main.variable(observer("d3")).define("d3", ["require"], function(require){return(
require("d3@5")
)});
  return main;
}
