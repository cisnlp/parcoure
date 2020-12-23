// https://observablehq.com/@d3/bar-chart@262
export default function define(runtime, observer) {
    const main = runtime.module();
    // const fileAttachments = new Map([["alphabet.csv",new URL("./alphabet.csv",import.meta.url)]]);
    // main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));

    const fileAttachments = new Map([["miserables.json",new URL("./stats.json",import.meta.url)]]);
    main.builtin("FileAttachment", runtime.fileAttachments(name => fileAttachments.get(name)));
    


    main.variable(observer()).define(["md"], function(md){return(
  md`# Bar Chart
  
  This chart shows the relative frequency of letters in the English language. This is a vertical bar chart, also known as a *column* chart. Compare to a [horizontal bar chart](/@d3/horizontal-bar-chart).`
  )});
    main.variable(observer("chart")).define("chart", ["d3","width","height","color","data","x","y","xAxis","yAxis"], function(d3,width,height,color,data,x,y,xAxis,yAxis)
  {
    const svg = d3.create("svg")
        .attr("viewBox", [0, 0, width, height]);
  
    svg.append("g")
        .attr("fill", color)
      .selectAll("rect")
      .data(data.counts)
      .join("rect")
        .attr("x", (d, i) => x(i))
        .attr("y", d => y(d.value))
        .attr("height", d => y(0) - y(d.value))
        .attr("width", x.bandwidth())
        .on("mouseover", d => {
          svg.style("cursor", "pointer");
        })
        .on("mouseout", d => {
          svg.style("cursor", "");
        })
        .on("click", (e, d) => {
          console.log(data.items[d.name]);
          $("#data").empty();
          
          $.each(data.items[d.name],  function( key, value ) {
            let par = jQuery('<div>', {"class":"row"})
            par.text(key + ": " + value)
            $('#data').append(par);
          });
          
        });

    svg.append("g")
        .call(xAxis);
  
    svg.append("g")
        .call(yAxis);
  
 

    return svg.node();
  }
  );
//     main.variable(observer("data")).define("data", ["d3","FileAttachment"], async function(d3,FileAttachment){return(
//   Object.assign(d3.csvParse(await FileAttachment("alphabet.csv").text(), ({letter, frequency}) => ({name: letter, value: +frequency})).sort((a, b) => d3.descending(a.value, b.value)), {format: "%", y: "↑ Frequency"})
//   )});
       main.variable(observer("data")).define("data", ["FileAttachment"], function(FileAttachment){return(
    FileAttachment("miserables.json").json()
    )});
    
    main.variable(observer("x")).define("x", ["d3","data","margin","width"], function(d3,data,margin,width){return(
  d3.scaleBand()
      .domain(d3.range(data.counts.length))
      .range([margin.left, width - margin.right])
      .padding(0.1)
  )});
    main.variable(observer("y")).define("y", ["d3","data","height","margin"], function(d3,data,height,margin){return(
  d3.scaleLinear()
      .domain([0, d3.max(data.counts, d => d.value)]).nice()
      .range([height - margin.bottom, margin.top])
  )});
    main.variable(observer("xAxis")).define("xAxis", ["height","margin","d3","x","data"], function(height,margin,d3,x,data){return(
  g => g
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x).tickFormat(i => data.counts[i].name).tickSizeOuter(0))
      .selectAll("text")
      .attr("transform", "translate(-10,10)rotate(-45)")
      .style("text-anchor", "end")
      .style("font-size", 14)
      .style("fill", "#69a3b2")
  )});
    main.variable(observer("yAxis")).define("yAxis", ["margin","d3","y","data"], function(margin,d3,y,data){return(
  g => g
      .attr("transform", `translate(${margin.left},0)`)
      .call(d3.axisLeft(y).ticks(null, data.counts.format))
      .call(g => g.select(".domain").remove())
      .call(g => g.append("text")
          .attr("x", -margin.left)
          .attr("y", 10)
          .attr("fill", "currentColor")
          .attr("text-anchor", "start")
          .text(data.counts.y))
  )});
    main.variable(observer("color")).define("color", function(){return(
  "steelblue"
  )});
    main.variable(observer("height")).define("height", function(){return(
  1000
  )});
    main.variable(observer("margin")).define("margin", function(){return(
  {top: 30, right: 0, bottom: 200, left: 40}
  )});
    main.variable(observer("d3")).define("d3", ["require"], function(require){return(
  require("d3@6")
  )});
    return main;
  }
  