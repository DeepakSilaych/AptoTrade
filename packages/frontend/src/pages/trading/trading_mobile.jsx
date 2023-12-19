import React from 'react'
import TradeAA from './component/tradeaa'
import TradeAB from './component/tradeab'
import TradeBAAA from './component/tradebaaa'
import TradeBAAB from './component/tradebaab'

function TradingMobile() {
  return (
    <Layout theme={theme} setTheme={setTheme} >
        <div className={style.trade}>
            <TradeAA curr={curr} />
            <TradeAB curr={curr} aptTicker={aptTicker} btcTicker={btcTicker} ethTicker={ethTicker}/>
            <TradeBAAA curr={curr} aptTicker={aptTicker} btcTicker={btcTicker} ethTicker={ethTicker}/>
            <TradeBAAB curr={curr} aptTicker={aptTicker} btcTicker={btcTicker} ethTicker={ethTicker}/>
      </div>
    </Layout>
  )
}

export default TradingMobile