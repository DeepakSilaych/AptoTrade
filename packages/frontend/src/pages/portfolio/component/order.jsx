import React, { useState, useEffect } from 'react';
import style from '../portfolio.module.css'
import {useSelector} from 'react-redux'
import {useWalletProvider} from '../../../context/walletContext'
import {useAddressProvider} from '../../../context/addressContext'

export default function OpenOrder() {
    const account = useSelector((state) => state.account)
    const {isConnected, setIsConnected} = useWalletProvider()
    const {address, setAddress} = useAddressProvider()
    const [orderToDelete, setOrderToDelete] = useState(null);
    const [showConfirmation, setShowConfirmation] = useState(false);

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

    const handleDeleteClick = (order) => {
      setOrderToDelete(order);
      setShowConfirmation(true);
    };
    return (
    <div className={style.position}>
        <h4>Open Orders</h4>
        <div style={{display:'flex', flexDirection:'column'}}>
            <div className={style.centertable}>
                <span>Instrument</span>
                <span>Type</span>
                <span>Size</span>
                <span>Direction</span>
                <span>Remaining</span>
                <span>Timestamp</span>
                <span>Cancel</span>
            </div>
            {isConnected ?
                <>
                {Object.keys(account.open_orders).map(function (key) {
                    return (
                      <>
                      {
                        Object.keys(account.open_orders[key]).map(function (orderKey) {
                          const order = account.open_orders[key][orderKey];
                          const timestamp = new Date(order.time).toLocaleString();
                          const cancelOrder = () => {
                          };
                          return (
                            <div className={style.centertablebody}>
                            <span>{account.positions[key].instrument_name}</span>
                            <span>{order.side}</span>
                            <span>{order.size}</span>
                            <span>{order.class}</span>
                            <span>{order.remainingToFill}</span>
                            <span>{timestamp}</span>
                            <button style={{ fontSize: '10px', color: 'red', cursor: 'pointer' }} onClick={() => handleDeleteClick(order)}>❌</button>
                            </div>
                            );
                          })
                        }
                      </>
                    )
                  })
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