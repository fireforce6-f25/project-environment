import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './HoursChart.css';

const HoursChart = () => {
  const svgRef = useRef();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5001/api/hours')
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

    // Convert data to array format for D3
    const chartData = Object.entries(data).map(([repo, info]) => ({
      repo,
      hours: info.total_hours
    })).sort((a, b) => b.hours - a.hours);

    const margin = { top: 40, right: 30, bottom: 120, left: 60 };
    const width = 800 - margin.left - margin.right;
    const height = 500 - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // X scale
    const x = d3.scaleBand()
      .domain(chartData.map(d => d.repo))
      .range([0, width])
      .padding(0.2);

    // Y scale
    const maxHours = Math.max(...chartData.map(d => d.hours), 1);
    const y = d3.scaleLinear()
      .domain([0, maxHours * 1.1])
      .range([height, 0]);

    // Color scale
    const color = d3.scaleOrdinal()
      .domain(chartData.map(d => d.repo))
      .range(d3.schemeSet2);

    // Add X axis
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end')
      .style('font-size', '12px')
      .style('fill', 'black');

    // Add Y axis
    svg.append('g')
      .call(d3.axisLeft(y).ticks(10))
      .selectAll('text')
      .style('font-size', '12px')
      .style('fill', 'black');

    // Y axis label
    svg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -45)
      .attr('x', -height / 2)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('fill', 'black')
      .text('Hours Worked');

    // Add bars
    svg.selectAll('.bar')
      .data(chartData)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.repo))
      .attr('y', d => y(d.hours))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.hours))
      .attr('fill', d => color(d.repo))
      .attr('rx', 4)
      .attr('ry', 4);

    // Add value labels on top of bars
    svg.selectAll('.label')
      .data(chartData)
      .enter()
      .append('text')
      .attr('class', 'bar-label')
      .attr('x', d => x(d.repo) + x.bandwidth() / 2)
      .attr('y', d => y(d.hours) - 5)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .style('fill', 'black')
      .text(d => d.hours > 0 ? d.hours.toFixed(1) : '0');

  }, [data]);

  if (loading) {
    return <div className="loading">Loading hours data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="hours-container">
      <h2>Hours Worked by Repository</h2>
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default HoursChart;
