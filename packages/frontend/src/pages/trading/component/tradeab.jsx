import React, {useEffect, useState} from 'react'
import PBlocks from '../../portfolio/component/pblock'
import style from "../trade.module.css"
import { useAppSelector } from '../../../redux/hooks';
import { useSelector } from 'react-redux';
import { useAppDispatch } from '../../../redux/hooks';
import { setPrice } from '../../../redux/features/priceSlice';

const Stats = ({ticker, curr}) => {
  return(
    <div className={style.tradeab}>
      <div className={style.blocks}>
        <div>Index Prices</div>
        <div>${ticker.index_price.toFixed(2)}</div>
      </div>
      <div className={style.blocks}>
        <div>Mark Prices</div>
        <div>${ticker.mark_price.toFixed(2)}</div>
      </div>
      <div className={style.blocks}>
        <div>High</div>
        <div>${ticker.stats.high.toFixed(2)}</div>
      </div>
      <div className={style.blocks}>
        <div>Low</div>
        <div>${ticker.stats.low.toFixed(2)}</div>
      </div>
      <div className={style.blocks}>
        <div>24hr Volume ({curr})</div>
        <div>{ticker.stats.volume.toFixed(2)}</div>
      </div>
      <div className={style.blocks}>
        <div>24h Volume(usd)</div>
        <div>${ticker.stats.volume_usd.toFixed(2)}</div>
      </div>
    </div>
  )
}

function TradeAB({curr, aptTicker, ethTicker, btcTicker}) {

  return(
    <PBlocks bwidth="70% " bheight="100%">
      <Stats ticker={curr === "apt" ? aptTicker : (curr === "btc" ? btcTicker: ethTicker)} curr={curr}/>
    </PBlocks>
    )
}

export default TradeAB