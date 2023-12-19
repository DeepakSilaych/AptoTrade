import React, { useEffect, useState } from 'react';
import PBlocks from '../../portfolio/component/pblock';
import style from '../trade.module.css';
import { useWalletProvider } from "../../../context/walletContext";
import { useAddressProvider } from "../../../context/addressContext";
import axios from 'axios'
import { useSelector } from 'react-redux'
import toast from 'react-hot-toast'

function TradeBB({ curr, aptTicker, ethTicker, btcTicker }) {
  return(
    <TradeBBchild ticker={curr === "apt" ? aptTicker : (curr === "btc" ? btcTicker: ethTicker)} curr={curr}/>
  );

}

function TradeBBchild({ticker,curr}) {
  const [buySellValue, setBuySellValue] = useState('Buy');
  const [orderTypeValue, setOrderTypeValue] = useState('Market');
  const [orderSize, setOrderSize] = useState(0);
  const [leverage, setLeverage] = useState(1);
  const [limitPrice, setLimitPrice] = useState(0);
  const {isConnected, setIsConnected} = useWalletProvider();
  const {address, setAddress} = useAddressProvider();
  const [availableMargin, setAvailableMargin] = useState(0.0);
  const [remainingMargin, setRemainingMargin] = useState(0)


  const account = useSelector((state) => state.account)


  // const [netOrderSize, setNetOrderSize] = useState(0)
  const notEnoughMargin = () => {
    toast.error("NOT ENOUGH MARGIN")
  }

  const [price, setPrice] = useState(0)

  useEffect(() => {
    if(ticker){
      setPrice(ticker.index_price)
      if(isConnected){
        let total = 0
        try{
          const btcMargin = account.positions["BTC-20DEC23"].margin || 0;
          const ethMargin = account.positions["ETH-20DEC23"].margin || 0;
          const aptMargin = account.positions["APT-20DEC23"].margin || 0;
          total = account.collateral- btcMargin-ethMargin-aptMargin;
        }catch{
          total = 0
        }
        setRemainingMargin(total)
      }
    }
  }, [ticker, isConnected, account])

  const apiUrl = 'http://localhost:8081/api/';
  
  const sendLimitOrder = async (amount, leverage) => {

    try {
      if(amount > remainingMargin){
        notEnoughMargin()
        return
      }
      let marketId = 1;
      let instrument_name;
      if(curr === 'eth'){
        instrument_name = "ETH-20DEC23"
        marketId =2
      }
      else if(curr === 'btc'){
        instrument_name = "BTC-20DEC23"
        marketId = 1
      }
      else if(curr === 'apt'){
        instrument_name = "APT-20DEC23"
        marketId = 3
      }

      const side = buySellValue === 'Buy' ? false : true

      const tx = {
        type: "entry_function_payload",
        function: "0x2da25555efbb5ac2c6d42a8a02228ba8f25e2b42b3eea9b35516578a43f2a62f::manager::place_limit_order_user_entry",
        arguments: [10000000000000, 1, "0x5aa5dac7818fefdf095b6001ec7f2607bd7576c8f9a74c5c1a342bad9e8cf889", side, Math.floor(amount * 100), (parseFloat(limitPrice).toFixed(2))*100],
        type_arguments: ["0x3f4111e71d011986d24815ce66ce35900c892561d8cf163c41af23100b7d55a7::btc::BTC","0x3f4111e71d011986d24815ce66ce35900c892561d8cf163c41af23100b7d55a7::usdc::USDC"]
      }

      await window.aptos.signAndSubmitTransaction(tx);
  
      const from = address
      const type = 'limit'
      const total = (amount*leverage/price).toFixed(2)
      const req = {
        jsonrpc: "2.0",
        id: 1,
        method: buySellValue === 'Buy' ? 'private/buy' : 'private/sell',
        params :{
          from,
          instrument_name,
          type,
          amount:total,
          leverage,
          price:limitPrice
        }
      }
      const resp = await axios.post(apiUrl, req )
      console.log(resp.data)
      if(resp.data.response[0] === 'Not enough margin'){
        notEnoughMargin()
      }
    } catch (e){
      console.log(e)
      return;
    } 


  }

  const sendMarketOrder = async (amount, leverage) => {

    try{

      if(amount > remainingMargin){
        notEnoughMargin()
        return
      }

      if(amount > remainingMargin){
        notEnoughMargin()
        return
      }
      let marketId = 1;
      let instrument_name;
      if(curr === 'eth'){
        instrument_name = "ETH-20DEC23"
        marketId =2
      }
      else if(curr === 'btc'){
        instrument_name = "BTC-20DEC23"
        marketId = 1
      }
      else if(curr === 'apt'){
        instrument_name = "APT-20DEC23"
        marketId = 3
      }

      const side = buySellValue === 'Buy' ? false : true
      const total = (amount*leverage/price).toFixed(2)

      const tx = {
        type: "entry_function_payload",
        function: "0x2da25555efbb5ac2c6d42a8a02228ba8f25e2b42b3eea9b35516578a43f2a62f::manager::place_market_order_user_entry",
        arguments: [Math.floor(total*1000000), 1, "0x5aa5dac7818fefdf095b6001ec7f2607bd7576c8f9a74c5c1a342bad9e8cf889", side],
        type_arguments: ["0x3f4111e71d011986d24815ce66ce35900c892561d8cf163c41af23100b7d55a7::btc::BTC","0x3f4111e71d011986d24815ce66ce35900c892561d8cf163c41af23100b7d55a7::usdc::USDC"]
      }

      await window.aptos.signAndSubmitTransaction(tx);

      console.log("executing")
      const from = address
      const type = 'market'
      console.log("executing2")
      const req = {
        jsonrpc: "2.0",
        id: 1,
        method: buySellValue === 'Buy' ? 'private/buy' : 'private/sell',
        params :{
          from,
          instrument_name,
          type,
          amount:total,
          leverage,
        }
      }
      console.log("executing3")
      console.log(req)
      const resp = await axios.post(apiUrl, req )
      if(resp.data.response[0] === 'Not enough margin'){
        notEnoughMargin()
      }
    }catch(e){
      console.log(e)
      return
    }
    let instrument_name;
    if(curr === 'eth'){
      instrument_name = "ETH-20DEC23"
    }
    else if(curr === 'btc'){
      instrument_name = "BTC-20DEC23"
    }
    else if(curr === 'apt'){
      instrument_name = "APT-20DEC23"
    }
  }

  const trade = async () => {
    if(orderTypeValue === "Limit"){
      await sendLimitOrder(orderSize, leverage, limitPrice ,price)
    }else{
      await sendMarketOrder(orderSize,leverage, price)
    }
  }



  const handleConnectWallet = async () => {
    const getAptosWallet = () => {
      if ('aptos' in window) {
        return window.aptos;
      } else {
        window.open('https://petra.app/', '_blank');
      }
    };

    const wallet = getAptosWallet();

    try {
      const response = await wallet.connect();

      setIsConnected(true);
      setAddress(response.address);

      alert(`Connected to Petra! Address: ${response.address}`);
    } catch (error) {
      // Handle errors
      console.error(error);
      alert('Failed to connect to Petra. Please try again.');
    }
  };
  const [showNegativeWarning, setShowNegativeWarning] = useState(false);

  // ... existing functions ...

  const handleOrderSizeChange = (e) => {
    const value = e.target.value;
    if (value < 0) {
      setShowNegativeWarning(true);
      setOrderSize(0); // Reset to 0 or keep the last valid value
    } else {
      setOrderSize(value);
      setShowNegativeWarning(false); // Hide warning if value is valid
    }
  };


  return (
    <PBlocks bwidth="22%" bheight="98.5%">
      <div className={style.tradebb}>
        <div className={style.buysell}>
          <span className={`${buySellValue === 'Buy' ? style.hoverbuy : style.hoversell}`} ></span>
          <div className={`${buySellValue === 'Buy' && style.buyactive}`} onClick={() => setBuySellValue('Buy')}>Buy</div>
          <div className={`${buySellValue === 'Sell' && style.sellactive}`} onClick={() => setBuySellValue('Sell')}>Sell</div>
        </div>
        <div className={style.marketlimit}>
          <span className={`${orderTypeValue === 'Market' && style.hoverleft}`} ></span>
          <div onClick={() => setOrderTypeValue('Market')}>Market</div>
          <div onClick={() => setOrderTypeValue('Limit')}>Limit</div>
        </div>
          <form>
            <div className={style.formcontent}>
                <label htmlFor="orderSize" style={{fontSize:'16px'}}>Order Size ($)</label>
            <input
              type="number"
              id="orderSize"
              value={orderSize}
              placeholder='0'
              style={{ marginTop: '10px' }}
              onChange={handleOrderSizeChange}
            />
            {showNegativeWarning && (
              <div style={{ color: 'red', marginTop: '2px' }}>
                Negative values not accepted!
              </div>
            )}
              <div style={{display:'flex', alignItems:'center', justifyContent:'right'}}>
              <span style={{ fontSize: '0.8rem', fontWeight: "400", color: buySellValue === 'Buy' ? 'lime' : 'red' }}>${ remainingMargin.toFixed(2)} Remaining</span>
              </div>
            </div>

            {orderTypeValue === 'Limit' && (
              <div className={style.formcontent}>
                <label htmlFor="limitPrice">Limit Price</label>
                <input
                  type="number"
                  id="limitPrice"
                  value={limitPrice}
                  placeholder='0'
                  onChange={(e) => setLimitPrice(e.target.value)}
                />
              </div>
            )}

            <div className={style.leverage}>
              <label htmlFor="leverage">Leverage</label>
              <div>
                <input
                  type="range"
                  id="leverage"
                  value={leverage}
                  min={1}
                  max={50}
                  onChange={(e) => setLeverage(e.target.value)}
                />
                <input 
                  type="integer"
                  value={leverage}
                  onChange={(e) => setLeverage(e.target.value)}
                />
              </div>
          </div>
          
          </form>
          <div className={style.formcontent} style={{display:'flex', flexDirection:'row', justifyContent:'space-around'}}>
              <label style={{fontSize:'1.2rem', fontWeight:'400', display:'flex',flexDirection:'column', height:'100%', justifyContent:'center'}}>Total</label>
              <div style={{display:'flex', flexDirection:'column'}}>
                <span style={{textAlign:'right', fontSize:'.9rem', color: buySellValue === 'Buy' ? 'lime': 'red'}}> ${(orderSize*leverage).toFixed(2)}</span>
                <span style={{textAlign:'right', marginTop:'.1rem', fontSize:'.9rem', color: buySellValue === 'Buy' ? 'lime': 'red'}}>{(orderSize*leverage/price).toFixed(2)} {curr}</span>
              </div>
            </div>

          {!isConnected ? 
                <div className={style.bbsideconnectdiv}>
                  <span className={style.sideconnected} onClick={handleConnectWallet}>Connect Wallet</span>
                </div>                
              : 
                <div className={style.sideconnected} style={{marginTop:'20px'}} onClick={trade}>Trade</div>
          }
      </div>
    </PBlocks>
  );
}

export default TradeBB;
