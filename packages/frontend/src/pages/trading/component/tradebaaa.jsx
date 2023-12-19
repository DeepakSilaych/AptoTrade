import PBlocks from '../../portfolio/component/pblock'
import React, { useEffect, useRef } from 'react';
import style from '../trade.module.css'

let tvScriptLoadingPromise;

export default function TradingViewWidget({curr, theme, setTheme}) {
  let chartBackground =0;
  if(theme==='light'){
    chartBackground = 1;
  }
  else {
    chartBackground = 2;
  }
  let heme
  if(chartBackground===1){ heme = 'white'}
  if(chartBackground===2){heme = '#12121A'}

  const onLoadScriptRef = useRef();
  let currcode;
  if(curr=== 'apt'){currcode = 'APTUSD'}
  if(curr=== 'btc'){currcode = 'BTCUSD'}
  if(curr=== 'eth'){currcode = 'ETHUSD'}

  useEffect(
    () => {
      onLoadScriptRef.current = createWidget;

      if (!tvScriptLoadingPromise) {
        tvScriptLoadingPromise = new Promise((resolve) => {
          const script = document.createElement('script');
          script.id = 'tradingview-widget-loading-script';
          script.src = 'https://s3.tradingview.com/tv.js';
          script.type = 'text/javascript';
          script.onload = resolve;

          document.head.appendChild(script);
        });
      }

      tvScriptLoadingPromise.then(() => onLoadScriptRef.current && onLoadScriptRef.current());

      return () => onLoadScriptRef.current = null;

      function createWidget() {
        if (document.getElementById('tradingview_ec0c5') && 'TradingView' in window) {
          new window.TradingView.widget({
            autosize: true,
            symbol: currcode,
            interval: "5",
            timezone: "Etc/UTC",
            theme: theme,
            style: "1",
            locale: "in",
            enable_publishing: false,
            withdateranges : true,
            hide_side_toolbar: false,
            allow_symbol_change : false,
            hide_legend: true,
            save_image: false,
            withdateranges: false,
            container_id: "tradingview_ec0c5",
            backgroundColor: heme,
            gridColor: heme,
          });
        }
      }
    },
    [theme, curr]
  );

  return (
    <div className={style.tradebaaa_tradingblock}>
      <div className='tradingview-widget-container' style={{ height: "100%", width: "100%" }}>
        <div id='tradingview_ec0c5' style={{ height: "calc(100% - 32px)", width: "100%" }} />
      </div>
    </div>
  )
}
