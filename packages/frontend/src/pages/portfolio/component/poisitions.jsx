import React, { useState, useEffect } from 'react';
import style from '../portfolio.module.css'
import {useSelector} from 'react-redux'
import {useWalletProvider} from '../../../context/walletContext'
import {useAddressProvider} from '../../../context/addressContext'

export default function Positions() {
    const account = useSelector((state) => state.account)
    const {isConnected, setIsConnected} = useWalletProvider()
    const {address, setAddress} = useAddressProvider()

    const initWalletFromLocalStorage = () => {
        const connected = localStorage.getItem('walletConnected') === 'true';
        const storedAddress = localStorage.getItem('walletAddress');
    
        if (connected && storedAddress) {
          setIsConnected(true);
          setAddress(storedAddress);
        }
      };
    
      useEffect(() => {
        initWalletFromLocalStorage();
      }, []);

    return (
    <div className={style.position}>
        <h4>Positions</h4>
        <div style={{display:'flex', flexDirection:'column'}}>
            <div className={style.centertable}>
                <span >Instrument</span>
                <span >Size</span>
                <span >Size ($)</span>
                <span >Direction</span>
                <span >Average Price</span>
                <span >PnL</span>
                <span >Liquidation Price</span>
            </div>
            {isConnected ?
                <>
                {
                    Object.keys(account.positions).map(function(key) {
                    return(
                        <>
                        {
                        Object.keys(account.positions[key]).length > 0 &&
                        <div className={style.centertablebody}>
                            <span>{key}</span>
                            <span>{account.positions[key].size}</span>
                            <span>${parseFloat(account.positions[key].size * account.positions[key].average_price).toFixed(2)}</span>
                            <span>{account.positions[key].direction}</span>
                            <span>${parseFloat(account.positions[key].average_price).toFixed(2)}</span>
                            <span style={{color: parseFloat(account.positions[key].unrealized_pnl) > 0 ? 'green': 'red'}}>${parseFloat(account.positions[key].unrealized_pnl).toFixed(2)}</span>
                            <span>${parseFloat(account.positions[key].estimated_liquidation_price).toFixed(2)}</span>
                        </div>
                        }
                        </>
                    )
                    }
                    )
                }
                </>
                :
                <div className={style.connectyourwallet}>
                    connect your wallet
                </div>
            }
        </div>
    </div>
    );
}