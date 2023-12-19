import React from 'react'
import PBlocks from '../../portfolio/component/pblock'  
import style from '../trade.module.css'
import { useWalletProvider } from "../../../context/walletContext";
import { useAddressProvider } from "../../../context/addressContext";
import { useSelector } from 'react-redux'


function TradeBAB({curr}) {

  const account = useSelector((state) => state.account)

  const {setAddress} = useAddressProvider()
  const {isConnected, setIsConnected} = useWalletProvider()
  const [tabs, setTabs] = React.useState(0);

  React.useEffect(() => {}, [account.positions])


  const handleConnectWallet = async () => {
    // Function to check if Petra is installed
    const getAptosWallet = () => {
      if ('aptos' in window) {
        return window.aptos;
      } else {
        window.open('https://petra.app/', '_blank');
      }
    };

    const wallet = getAptosWallet();

    try {
      // Connect to Petra
      const response = await wallet.connect();

      // Set the connection status and wallet address
      setIsConnected(true);
      setAddress(response.address);

      // Do something with the connected wallet, e.g., update UI
      alert(`Connected to Petra! Address: ${response.address}`);
    } catch (error) {
      // Handle errors
      console.error(error);
      alert('Failed to connect to Petra. Please try again.');
    }
  };


  return (
      <PBlocks bwidth="99%" bheight="35%">
        <div className={style.tradebab}>
            <div style={{display: 'flex',width:'28%', alignItems:'center', justifyContent:'left', marginTop: '10px', backgroundColor:'#18181F', borderRadius:'10px'}}>
              <div onClick={() => {setTabs(0)}} style={{cursor:'pointer',backgroundColor: tabs === 0?'#1E1E24': '#18181F', padding:'8px', paddingLeft:'15px', paddingRight:'15px', fontSize:'10px', borderRadius:'8px'}}>Positions</div>
              <div onClick={() => {setTabs(1)}} style={{cursor:'pointer',marginLeft:'15px', backgroundColor: tabs === 1?'#1E1E24': '#18181F', padding:'8px', paddingLeft:'15px', paddingRight:'15px', fontSize:'10px', borderRadius:'8px'}}>Orders</div>
              <div onClick={() => {setTabs(2)}} style={{cursor:'pointer',marginLeft:'15px', backgroundColor: tabs === 2?'#1E1E24': '#18181F', padding:'8px', paddingLeft:'15px', paddingRight:'15px', fontSize:'10px', borderRadius:'8px'}}>Trades</div>
            </div>
        <div>
          {isConnected
            &&
            <>
             {
                tabs === 0 &&
                <div style={{display:'flex', flexDirection:'column'}}>
                  <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginTop:'20px',paddingLeft:'15px', paddingRight:'15px'}}>
                    <span style={{fontSize:'10px'}}>Instrument</span>
                    <span style={{fontSize:'10px'}}>Size</span>
                    <span style={{fontSize:'10px'}}>Size ($)</span>
                    <span style={{fontSize:'10px'}}>Direction</span>
                    <span style={{fontSize:'10px'}}>Average Price</span>
                    <span style={{fontSize:'10px'}}>PnL</span>
                    <span style={{fontSize:'10px'}}>Liquidation Price</span>
                  </div>
                  {
                    Object.keys(account.positions).map(function(key) {
                      return(
                        <>
                        {
                        Object.keys(account.positions[key]).length > 0 &&
                          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginTop:'15px', backgroundColor:'#1E1E24', borderRadius:'12px', padding:'10px', paddingLeft:'15px', paddingRight:'15px'}}>
                            <span style={{fontSize:'10px'}}>{key}</span>
                            <span style={{fontSize:'10px'}}>{account.positions[key].size}</span>
                            <span style={{fontSize:'10px'}}>${parseFloat(account.positions[key].size * account.positions[key].average_price).toFixed(2)}</span>
                            <span style={{fontSize:'10px'}}>{account.positions[key].direction}</span>
                            <span style={{fontSize:'10px'}}>${parseFloat(account.positions[key].average_price).toFixed(2)}</span>
                            <span style={{fontSize:'10px', color: parseFloat(account.positions[key].unrealized_pnl) > 0 ? 'green': 'red'}}>${parseFloat(account.positions[key].unrealized_pnl).toFixed(2)}</span>
                            <span style={{fontSize:'10px'}}>${parseFloat(account.positions[key].estimated_liquidation_price).toFixed(2)}</span>
                          </div>
                        }
                        </>
                      )
                      }
                    )
                  }
                </div>
              }
            {
              tabs === 1 &&
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '20px', paddingLeft: '15px', paddingRight: '15px' }}>
                  <span style={{ fontSize: '10px' }}>Instrument</span>
                  <span style={{ fontSize: '10px' }}>Type</span>
                  <span style={{ fontSize: '10px' }}>Size</span>
                  <span style={{ fontSize: '10px' }}>Direction</span>
                  <span style={{ fontSize: '10px' }}>Remaining</span>
                  <span style={{ fontSize: '10px' }}>Timestamp</span>
                  <span style={{ fontSize: '10px' }}>Cancel</span>
                </div>
                {
                  Object.keys(account.open_orders).map(function (key) {
                    return (
                      <>
                        {
                          Object.keys(account.open_orders[key]).map(function (orderKey) {
                            const order = account.open_orders[key][orderKey];
                            const timestamp = new Date(order.time).toLocaleString();
                            return (
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '15px', backgroundColor: '#1E1E24', borderRadius: '12px', padding: '10px', paddingLeft: '15px', paddingRight: '15px' }}>
                                <span style={{ fontSize: '10px' }}>{account.positions[key].instrument_name}</span>
                                <span style={{ fontSize: '10px' }}>{order.side}</span>
                                <span style={{ fontSize: '10px' }}>{order.size}</span>
                                <span style={{ fontSize: '10px' }}>{order.class}</span>
                                <span style={{ fontSize: '10px' }}>{order.remainingToFill}</span>
                                <span style={{ fontSize: '10px' }}>{timestamp}</span>
                                <span style={{ fontSize: '10px' }}>{order.is_liquidation ? order.is_liquidation.toString() : "N/A"}</span>
                              </div>
                            );
                          })
                        }
                      </>
                    )
                  })
                }
              </div>
            }

           </>
            // <>
            //   <thead>
            //     <tr>
            //       <th>Instrument</th>
            //       <th>Size (eth)</th>
            //       <th>Size ($)</th>
            //       <th>LastAmount</th>
            //       <th>Direction</th>
            //       <th>Average Price</th>
            //       <th>PnL</th>
            //       <th>Liquidation Price</th>
            //     </tr>
            //   </thead>
            //   <tbody className={style.tradebab_table_data}>
            //     {/* {orderdata.map((user, index)=>(
            //       <tr key={index}>
            //         <td>{user.Symbol}</td>
            //         <td>{user.ID}</td>
            //         <td>{user.LastAmount}</td>
            //         <td>{user.Price}</td>
            //         <td className={`${user.Side==="Buy" ? style.positiongreen : style.positionred}`}>{user.Side}</td>
            //         <td>{user.Profit}</td>
            //         <td>{user.Type}</td>
            //       </tr>
            //     ))} */}
            //   </tbody>
            // </>
          }
          {
            !isConnected &&
            <div className={style.babsideconnectdiv} >
              <span class= { style.sideconnect} onClick={handleConnectWallet}>Connect Wallet</span>
            </div>     
          }
        </div>
        </div>
      </PBlocks>
  )
}

export default TradeBAB;
