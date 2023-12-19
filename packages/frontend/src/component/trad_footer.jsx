import React, { useState, useEffect } from 'react'
import style from './style.module.css'
import { Link } from 'react-router-dom'

function TFooter() {
    const [operational, setoperational] = useState(1);
    const [utcTime, setUtcTime] = useState('');

    useEffect(() => {
        const updateUtcTime = () => {
        const currentDate = new Date();
        const utcTimeString = currentDate.toISOString().slice(0, 19).replace('T', ' '); // Format: YYYY-MM-DDTHH:mm:ss
        setUtcTime(utcTimeString);
        };
        const intervalId = setInterval(updateUtcTime, 1000); 

        return () => clearInterval(intervalId);
    }, []);
    return (

    <div className={style.footer}>
        <div>
            { operational===0 ? 
                <Link to='/status' className={style.notoperational}><div className={style.status}></div>Systems are Down &#8599;</Link>
                : 
                <Link to='/status' className={style.operational}><div className={style.status}></div>Systems Operational &#8599;</Link>
            } 
        </div>
        <div className={style.time}>
            {utcTime}<p> UTC</p>
        </div>
    </div>
  )
}

export default TFooter