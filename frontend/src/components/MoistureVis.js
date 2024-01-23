import styles from './vis.module.css';
import { React, useState, useEffect, useRef } from "react";
import axios from 'axios';
import * as d3 from 'd3';

function MoistureVis() {

    const chartRef = useRef(null);
    const [soilData, setSoilData] = useState([]);
    const [soilData2, setSoilData2] = useState([]);
    const [soilData3, setSoilData3] = useState([]);
    const [ctime, setCtime] = useState("0");

    const fetchData = () => {
        axios.get(`http://samuraimain.ddns.net:8080/get_moisture`)
            .then((response) => {
                const newData = response.data;

                // Calculate the time difference with the first element
                const firstTimestamp = new Date(newData[0][0].time * 1000);
                const timeDifference = firstTimestamp.getTime() / 1000; // in seconds

                // Adjust the time values in newData
                const filtered = newData[0].map(item => ({
                    value: item.value,
                    time: (item.time - timeDifference)/3600
                }));
                const filtered2 = newData[1].map(item => ({
                    value: item.value,
                    time: (item.time - timeDifference)/3600
                }));
                const filtered3 = newData[2].map(item => ({
                    value: item.value,
                    time: (item.time - timeDifference)/3600
                }));
                // Set the adjusted data to the state
                setSoilData(filtered);
                setSoilData2(filtered2);
                setSoilData3(filtered3);
                // Set the first timestamp as Ctime
                setCtime(firstTimestamp.toLocaleString());
            })
            .catch((error) => {
                console.error(error);
            });
    };

    // Use useEffect to run the fetchData function on mount and every 10 seconds
    useEffect(() => {
        fetchData(); // Initial API call

        const intervalId = setInterval(() => {
            fetchData(); // API call every 10 seconds
        }, 2000);

        // Cleanup function to clear the interval on component unmount
        return () => clearInterval(intervalId);
    }, []); // The empty dependency array ensures that the effect runs only on mount and unmount


    useEffect(() => {
        // Check if an element with ID 'moist' already exists and remove it
        const existingSvg = d3.select('#moist');
        if (!existingSvg.empty()) {
            existingSvg.remove();
        }

        const width = 928;
        const height = 500;
        const marginTop = 20;
        const marginRight = 30;
        const marginBottom = 30;
        const marginLeft = 40;

        // Set up the SVG container
        const svg = d3.select(chartRef.current)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr("viewBox", [0, 0, width, height])
            .attr("style", "max-width: 100%; height: auto; height: intrinsic;")
            .attr('id', 'moist'); // Set the ID of the new SVG


        const x = d3.scaleLinear([d3.min(soilData, d => d.time), d3.max(soilData, d => d.time)], [marginLeft, width - marginRight]);
        const y = d3.scaleLinear([0, 100], [height - marginBottom, marginTop]);

        const line = d3.line()
            .x(d => x(d.time))
            .y(d => y(d.value));

        svg.append("g")
            .attr("transform", `translate(0,${height - marginBottom})`)
            .call(d3.axisBottom(x).ticks(width / 80).tickSizeOuter(0))
            .call(g => g.append("text")
                .attr("x", (width - marginRight) / 2 - 50)
                .attr("y", marginBottom)
                .attr("fill", "currentColor")
                .attr("text-anchor", "start")
                .text("Hours Since\n" + ctime));

        svg.append("g")
            .attr("transform", `translate(${marginLeft},0)`)
            .call(d3.axisLeft(y).ticks(height / 40))
            .call(g => g.select(".domain").remove())
            .call(g => g.selectAll(".tick line").clone()
                .attr("x2", width - marginLeft - marginRight)
                .attr("stroke-opacity", 0.1))
            .call(g => g.append("text")
                .attr("x", -marginLeft)
                .attr("y", 10)
                .attr("fill", "currentColor")
                .attr("text-anchor", "start")
                .text("Soil Moisture %"));

        // Append the line to the SVG
        svg.append('path')
            //.data([data])
            .attr('d', line(soilData))
            .attr('stroke', 'lightblue')
            .attr('fill', 'none');
        svg.append('path')
            //.data([data])
            .attr('d', line(soilData2))
            .attr('stroke', 'blue')
            .attr('fill', 'none');
        svg.append('path')
            //.data([data])
            .attr('d', line(soilData3))
            .attr('stroke', 'darkblue')
            .attr('fill', 'none');
    }, [chartRef, soilData, soilData2, soilData3, ctime]);


    return (
        <div className={styles.moistcont}>
            <div style={{ display: 'flex', justifyContent: 'center', columnGap: '20px', fontWeight: 'bold' }}>
                <div>Moisture</div>
                <div style={{ height: '25px', width:'25px', backgroundColor:'lightblue', border:'solid black 1px', borderRadius:'2px', color:'white', fontSize:'medium' }}>A1</div>
                <div style={{ height: '25px', width:'25px', backgroundColor:'blue', border:'solid black 1px', borderRadius:'2px', color:'white', fontSize:'medium' }}>A2</div>
                <div style={{ height: '25px', width:'25px', backgroundColor:'darkblue', border:'solid black 1px', borderRadius:'2px', color:'white', fontSize:'medium' }}>A3</div>
            </div>
            <div ref={chartRef} className={styles.msctn}>

            </div>
        </div>

    );
}

export default MoistureVis;
