import React, {useEffect, useState} from 'react'
import style from './trade.module.css'
import TradeAA from './component/tradeaa'
import TradeBAB from './component/tradebab'
import TradeBB from './component/tradebb'
import TradeBAAA from './component/tradebaaa'
import TradeBAAB from './component/tradebaab'
import TradeAB from './component/tradeab'
import Layout from '../../component/layout'

function Trading({theme, setTheme, curr}) {
  const [windowwidth, setWindowWidth] = useState(window.innerWidth);

  const initialTicker = {
    index_price: 0,
    mark_price: 0,
    stats:{
      high: 0,
      low: 0,
      volume: 0,
      volume_usd:0
    }
  }


  const [ethTicker, setEthTicker] = useState(initialTicker)
  const [btcTicker, setBtcTicker] = useState(initialTicker)
  const [aptTicker, setAptTicker] = useState(initialTicker)
  

  useEffect(() => {
    const init = async () => {
      const ws = new WebSocket('ws://127.0.0.1:8082/ticker/1234sjh29');
      ws.onopen = () => {
        ws.onmessage = (msg) => {
          const resp = JSON.parse(msg.data)
          
            if(resp.channel.includes("ticker.BTC")){
              setBtcTicker(resp.data)
            }
            if(resp.channel.includes("ticker.ETH")){
              setEthTicker(resp.data)
            }
            if(resp.channel.includes("ticker.APT")){
              setAptTicker(resp.data)
            }
        }
      }
    }
    init();
  }, []);

  return (
    <Layout theme={theme} setTheme={setTheme} >
      {windowwidth > 900 ?
        <div className={style.trade}>
            <div className={style.tradea}>
              <TradeAA curr={curr}/>
              <TradeAB curr={curr} aptTicker={aptTicker} btcTicker={btcTicker} ethTicker={ethTicker}/>
            </div>
            <div className={style.tradeb}>
              <div className={style.tradeba}>
                <dir className={style.tradebaa}>
                  <TradeBAAA theme={theme} setTheme={setTheme} curr={curr} />
                
                </dir>
                <TradeBAB curr={curr}/>
              </div>
              <TradeBAAB curr={curr} ticker={curr === "apt" ? aptTicker : (curr === "btc"? btcTicker : ethTicker)}/>
              <TradeBB curr={curr} aptTicker={aptTicker} btcTicker={btcTicker} ethTicker={ethTicker}/>          
            </div>
        </div>:
        <div className={style.trademobile}>
          <div className={style.tradema}>
            <TradeAA curr={curr}/>
            <TradeAB curr={curr} aptTicker={aptTicker} btcTicker={btcTicker} ethTicker={ethTicker}/>
          </div>
          <div>
            <TradeBAAA curr={curr} aptTicker={aptTicker} btcTicker={btcTicker} ethTicker={ethTicker}/>
            <TradeBAAB curr={curr} ticker={curr === "apt" ? aptTicker : (curr === "btc"? btcTicker : ethTicker)}/>
          </div>
        </div>
      }
    </Layout>
  )
}

export default Trading