import React, { useEffect, useState } from 'react'
import style from '../trade.module.css'
import { NavLink } from 'react-router-dom'
import PBlocks from '../../portfolio/component/pblock'
import axios from 'axios'

function TradeAA({curr}) {

  const [instruments, setInstruments] = useState([])
  
  async function init(){
    const headers = {"Content-Type": "application/json"}
    const req= {
      "jsonrpc": "string",
      "id": 0,
      "method": "public/get_all_instrument_names",
      "params": {}
    }
    const resp = await axios.post('http://127.0.0.1:8081/api', req)
    setInstruments(resp.data.response)
  }

  useEffect(() => {init()}, [])



  return (
      <PBlocks bwidth="30%" bheight="100%" >
        <div className={style.tradeaa}>
          <NavLink to="/trading/apt" className={`${curr==="apt" ? style.aaactive : style.aainactive} `}>{instruments[2]}</NavLink>
          <NavLink to="/trading/btc" className={`${curr==="btc" ? style.aaactive : style.aainactive} `}>{instruments[0]}</NavLink>
          <NavLink to="/trading/eth" className={`${curr==="eth" ? style.aaactive : style.aainactive} `}>{instruments[1]}</NavLink>
        </div>
      </PBlocks>
  );
}

export default TradeAA

