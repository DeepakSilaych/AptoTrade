import React, { useState, useEffect } from 'react'
import style from '../portfolio.module.css'
import CircularProgressBar from '../../../component/progressbar';
import { useSelector } from 'react-redux'
import {useWalletProvider} from '../../../context/walletContext'
import {useAddressProvider} from '../../../context/addressContext'


export default function Overview(theme) {
  const account = useSelector((state) => state.account)

  const {isConnected, setIsConnected} = useWalletProvider()
  const {address, setAddress} = useAddressProvider()

  useEffect(() => {}, [account.collateral, isConnected])
  
  const btcMargin = account.positions["BTC-20DEC23"]?.margin || 0;
  const ethMargin = account.positions["ETH-20DEC23"]?.margin || 0;
  const aptMargin = account.positions["APT-20DEC23"]?.margin || 0;
  const totalMargin = btcMargin + ethMargin + aptMargin;
  const availableMargin = account.collateral - totalMargin;

  const btcUnrealizedPnl = account.positions["BTC-20DEC23"]?.unrealized_pnl || 0;
  const ethUnrealizedPnl = account.positions["ETH-20DEC23"]?.unrealized_pnl || 0;
  const aptUnrealizedPnl = account.positions["APT-20DEC23"]?.unrealized_pnl || 0;
  const livePnL = btcUnrealizedPnl + ethUnrealizedPnl + aptUnrealizedPnl;

    const item = {
      img: "https://via.placeholder.com/150",
      name: "BTC",
      balance: "0.00000000",
      composition: "0.00%",
      value: "0.00",
    };

  

    const overviewdata = [
      { title: "Available Margin", amount: account.available_margin.toFixed(2) },
      { title: "Live PnL", amount: livePnL.toFixed(2) },
      { title: "Realised PnL", amount: "0" },
      { title: "Profit Factor", amount: "0" },
    ];
    const progressBarColors =
      theme === "dark"
        ? {
            activeStrokeColor: "white",
            inactiveStrokeColor: "rgba(255,255,255,0.2)",
            backgroundColor: "rgb(18,18,26)",
            textColor: "white",
          }
        : {
            activeStrokeColor: "white",
            inactiveStrokeColor: "rgba(0,0,0,0.2)",
            backgroundColor: "#DEE4E7",
            textColor: "black",
          };
          
  const utilizationPercentage = parseFloat(((account.collateral - availableMargin) / account.collateral) * 100);

  if(utilizationPercentage === NaN){
    utilizationPercentage = 0
  }

    return (
      <div className={style.portfoliooverview}>
        <h4>Portfolio Overview</h4>
        <div className={style.equity}>
          <h5 className={style.headlite}>Equity</h5>
          <div>
            <div>{!isConnected ? '0' : parseFloat(account.collateral, 2)}</div>
            <div style={{ color: "lime" }}>+0.00%</div>
          </div>
        </div>
  
        <div className={style.progressbar}>
          <CircularProgressBar
            selectedValue={!isConnected ? 0 : utilizationPercentage.toFixed(2)}
            maxValue={100}
            title="Margin Utilization"
          />
          <p>Utilization Percentage: {!isConnected ? 0 : utilizationPercentage.toFixed(2)}%</p>
        </div>
  
        <div className={style.overviewdata}>
          {overviewdata.map((item, index) => (
            <div key={index}>
              <div>{item.title}</div>
              <div>{item.amount}</div>
            </div>
          ))}
        </div>
  
        <div>
          <h5>Collateral</h5>
          <table>
            <thead>
              <tr>
                <th>Asset</th>
                <th>Balance</th>
                <th>Value</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className={style.td1}>
                  <span>USDC</span>
                </td>
                <td>{isConnected ? account.collateral : 0}</td>
                <td className={style.td1}>$1</td>
                <td className={style.action}>
                  <div>Faucet</div>
                  <div>Withdraw</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    );
  }