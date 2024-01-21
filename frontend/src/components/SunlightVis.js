import styles from './vis.module.css';
import { React, useState, useEffect, useRef } from "react";
import axios from 'axios';
import * as d3 from 'd3';

function SunlightVis() {

    const chartRef = useRef(null);
    const [soilData, setSoilData] = useState([]);
    const [ctime, setCtime] = useState("0");

    const fetchData = () => {
        axios.get(`http://samuraimain.ddns.net:8080/get_sunlight`)
            .then((response) => {
                const newData = response.data;

                // Calculate the time difference with the first element
                const firstTimestamp = new Date(newData[0].time * 1000);
                const timeDifference = firstTimestamp.getTime() / 1000; // in seconds

                // Adjust the time values in newData
                const filtered = newData.map(item => ({
                    value: item.value,
                    time: item.time - timeDifference
                }));
                console.log(filtered)
                // Set the adjusted data to the state
                setSoilData(filtered);
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
        const existingSvg = d3.select('#sun');
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
            .attr('id', 'sun'); // Set the ID of the new SVG


        const x = d3.scaleLinear([d3.min(soilData, d => d.time), d3.max(soilData, d => d.time)], [marginLeft, width - marginRight]);
        const y = d3.scaleLinear([0, 2000], [height - marginBottom, marginTop]);

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
                .text("Seconds Since\n" + ctime));

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
                .text("Sun Exposure (Lux)"));

        // Append the line to the SVG
        svg.append('path')
            //.data([data])
            .attr('d', line(soilData))
            .attr('stroke', 'red')
            .attr('fill', 'none');
    }, [chartRef, soilData, ctime]);


    return (
        <div className={styles.moistcont}>
            <div>Sun Exposure</div>
            <div ref={chartRef} className={styles.msctn}>

            </div>
        </div>

    );
}

export default SunlightVis;
