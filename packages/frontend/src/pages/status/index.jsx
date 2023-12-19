import React, { useState } from 'react'
import style from './status.module.css'
import data from './data'

function Status() {
    const [operational, setoperational] = useState(1);
    return (
      <div>
        <div className={style.container}>
            <div  className={style.head}>
            { operational===0 ? 
                <div className={style.notoperational}>All Systems <span>Not Operational</span></div>
                : 
                <div className={style.operational}>All Systems <span>Operational</span></div>
            }
            </div>
         
            <h2>Uptime over the past 90 days</h2>
            <div className={style.timelinecontainer}>
                <div className={style.timelineblock}>
                    <h3>Server</h3>
                    <Timeline data={data} />
                </div>
                <div className={style.timelineblock}>
                    <h3>Frontend</h3>
                    <Timeline data={data} />
                </div>
            </div>

            <div>
                <h1>Past Incidents</h1>
                <ul>
                    {data.map((entry) => (
                        <li key={entry.day} className={style.statuslist}>
                            <span className={style.listday}>{entry.day}</span>
                            <hr />
                            <span className={style.listdescription}>{entry.description}</span>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
      </div>
    );
  }
  
  export default Status;
  


  function Timeline({data}){
    return(
    <>
        <div className={style.timeline}>
            {data.map((entry) => (
            <div key={entry.day} className={style.statusDiv}>
                <div
                className={
                    entry.status === 0
                    ? style.colorGrey
                    : entry.status === 1
                    ? style.colorLime
                    : style.colorRed
                }
                ></div>
                <div className={style.hoverContent}>
                <span className={style.day}>{entry.day}</span>
                <span className={style.description}>{entry.description}</span>
                </div>
            </div>
            ))}
        </div>
        <div className={style.timelinebar}>
            <span>90 days ago</span>
            <hr />
            <span>100.0 % uptime</span>
            <hr />
            <span>Today</span>
        </div>
    </>
    )
  }