import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './DependencyGraph.css';

const DependencyGraph = () => {
  const svgRef = useRef();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch graph data from backend
    fetch('http://localhost:5001/api/graph')
      .then(response => response.json())
      .then(result => {
        if (result.success) {
          setData(result.data);
          setLoading(false);
        } else {
          setError(result.error);
          setLoading(false);
        }
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!data || !svgRef.current) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const width = 1200;
    const height = 800;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);

    // Create a container group for zooming
    const g = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Pin project-environment to the center
    const centerNode = data.nodes.find(n => n.id === 'project-environment');
    if (centerNode) {
      centerNode.fx = width / 2;
      centerNode.fy = height / 2;
    }

    // Create force simulation with spacing for larger nodes
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links)
        .id(d => d.id)
        .distance(180))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(80))
      .force('radial', d3.forceRadial(250, width / 2, height / 2).strength(0.3));

    // Define colors for version compatibility
    const edgeColors = {
      green: '#4CAF50',
      yellow: '#FFC107',
      red: '#F44336',
      gray: '#9E9E9E'
    };

    // Create arrow markers for each color
    const defs = svg.append('defs');
    Object.entries(edgeColors).forEach(([colorName, colorValue]) => {
      defs.append('marker')
        .attr('id', `arrow-${colorName}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 60)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', colorValue);
    });

    // Create links with color based on version compatibility
    const link = g.append('g')
      .selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('class', 'link')
      .attr('stroke', d => edgeColors[d.color] || edgeColors.gray)
      .attr('stroke-width', 2)
      .attr('marker-end', d => `url(#arrow-${d.color || 'gray'})`);

    // Create link labels for dependency versions
    const linkLabel = g.append('g')
      .selectAll('text')
      .data(data.links)
      .enter().append('text')
      .attr('class', 'link-label')
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .style('fill', '#666')
      .style('background', 'white')
      .style('pointer-events', 'none')
      .text(d => d.requiredVersion || '');

    // Create nodes
    const node = g.append('g')
      .selectAll('g')
      .data(data.nodes)
      .enter().append('g')
      .attr('class', 'node');

    // Add circles to nodes (larger to fit name + version)
    node.append('circle')
      .attr('r', 55)
      .attr('fill', d => {
        // Color nodes based on whether they have dependencies
        const hasOutgoing = data.links.some(l => l.source.id === d.id || l.source === d.id);
        const hasIncoming = data.links.some(l => l.target.id === d.id || l.target === d.id);
        if (hasOutgoing && hasIncoming) return '#4CAF50';
        if (hasOutgoing) return '#2196F3';
        if (hasIncoming) return '#FF9800';
        return '#9E9E9E';
      });

    // Add repo name inside the node
    node.append('text')
      .text(d => d.name)
      .attr('x', 0)
      .attr('y', -3)
      .attr('text-anchor', 'middle')
      .attr('class', 'node-name')
      .style('font-size', '10px')
      .style('fill', 'white')
      .style('font-weight', 'bold')
      .style('pointer-events', 'none');

    // Add version as subtitle below the name
    node.append('text')
      .text(d => d.version || 'unversioned')
      .attr('x', 0)
      .attr('y', 10)
      .attr('text-anchor', 'middle')
      .attr('class', 'node-version')
      .style('font-size', '9px')
      .style('fill', 'rgba(255,255,255,0.8)')
      .style('pointer-events', 'none');

    // Add title for hover
    node.append('title')
      .text(d => {
        const outgoing = data.links.filter(l =>
          (l.source.id === d.id || l.source === d.id)
        ).map(l => l.target.id || l.target);
        const incoming = data.links.filter(l =>
          (l.target.id === d.id || l.target === d.id)
        ).map(l => l.source.id || l.source);

        let tooltip = `${d.name}\n`;
        if (outgoing.length > 0) tooltip += `\nDepends on: ${outgoing.join(', ')}`;
        if (incoming.length > 0) tooltip += `\nDepended on by: ${incoming.join(', ')}`;
        return tooltip;
      });

    // Update positions on each tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      linkLabel
        .attr('x', d => (d.source.x + d.target.x) / 2)
        .attr('y', d => (d.source.y + d.target.y) / 2);

      node
        .attr('transform', d => `translate(${d.x},${d.y})`);
    });


    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [data]);

  if (loading) {
    return <div className="loading">Loading dependency graph...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="graph-container">
      <div className="legend">
        <h3>Nodes</h3>
        <div className="legend-item">
          <div className="legend-color" style={{backgroundColor: '#2196F3'}}></div>
          <span>Has dependencies only</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{backgroundColor: '#FF9800'}}></div>
          <span>Is depended upon only</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{backgroundColor: '#4CAF50'}}></div>
          <span>Both</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{backgroundColor: '#9E9E9E'}}></div>
          <span>No connections</span>
        </div>
      </div>
      <div className="legend legend-arrows">
        <h3>Version Compatibility</h3>
        <div className="legend-item">
          <div className="legend-arrow" style={{backgroundColor: '#4CAF50'}}></div>
          <span>Exact match</span>
        </div>
        <div className="legend-item">
          <div className="legend-arrow" style={{backgroundColor: '#FFC107'}}></div>
          <span>Minor/patch mismatch</span>
        </div>
        <div className="legend-item">
          <div className="legend-arrow" style={{backgroundColor: '#F44336'}}></div>
          <span>Major version mismatch</span>
        </div>
        <div className="legend-item">
          <div className="legend-arrow" style={{backgroundColor: '#9E9E9E'}}></div>
          <span>Unknown version</span>
        </div>
      </div>
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default DependencyGraph;
