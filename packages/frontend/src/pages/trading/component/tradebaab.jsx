import React, { useEffect } from 'react';
import style from '../trade.module.css';

function TradeBAAB({curr, ticker}) {
  const [sdata, setSData] = React.useState([]);
  const [bdata, setBData] = React.useState([]);


  useEffect(() => {
    // setSData(ethTicker.asks.slice(0,10))
    if(ticker.asks){
      setSData(ticker.asks.slice(0,8))
      setBData(ticker.bids.slice(0,8))
    }
  }, [ticker]);

  const sellData = sdata.map((user) => {
    return {
      price: user[0],
      size: user[1],
      cumulative: 0,
    };
  });

  const buyData = bdata.map((user) => {
    return {
      price: user[0],
      size: user[1],
      cumulative: 0,
    };
  });


  for (let i = 0; i < sellData.length; i++) {
    if (i ===0) {
      sellData[i].cumulative = parseInt(sellData[i].size, 10);
      continue;
    }
    const cumulativeValue = sellData[i - 1].cumulative + parseInt(sellData[i].size, 10);
    sellData[i].cumulative = cumulativeValue;
  }

  for (let i = 0; i < buyData.length; i++) {
    if (i === 0) {
      buyData[i].cumulative = parseInt(buyData[i].size, 10);
      continue;
    }
    const cumulativeValue = buyData[i - 1].cumulative + parseInt(buyData[i].size, 10);
    buyData[i].cumulative = cumulativeValue; 
  }

  return (
    <div className={style.Tradebaab}>
      <div className={style.tradebaab_order}>Orderbook</div>
      <table className={style.table}>
        <thead>
          <tr>
            <th>Price</th>
            <th>Size ({curr.toUpperCase()})</th>
            <th>Sum ({curr.toUpperCase()})</th>
          </tr>
        </thead>
        <tbody>
        <div style={{marginTop: '20px'}} />
          {sellData.reverse().map((user, index) => (
            <tr key={index} style={{ color: 'red' }}>
              <td style={{ color: '#C00C45' }}>${user.price.toFixed(2)}</td>
              <td>{user.size}</td>
              <td>
                {user.cumulative}
                <div className={style.redorderbg} style={{ width: `${user.cumulative/200}%` }}></div>
              </td>
            </tr>
          ))}
          <div style={{marginTop: '20px'}} />
          {buyData.map((user, index) => (
            <tr key={index}>
              <td style={{ color: '#05B306' }}>${user.price.toFixed(2)}</td>
              <td>{user.size}</td>
              <td>
                {user.cumulative}
                <div className={style.greenorderbg} style={{ width: `${user.cumulative/200}%` }}></div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
export default TradeBAAB;
