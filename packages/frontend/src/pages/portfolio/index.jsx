import React, { useState, useEffect } from 'react'
import style from './portfolio.module.css'
import PBlocks from './component/pblock'
import btc from './component/btc.svg'
import eth from './component/eth.svg'
import apt from './component/apt.svg'
import { Globe, Layers, AlignLeft, History, User } from 'lucide-react';
import Layout from '../../component/layout'
import {useWalletProvider} from '../../context/walletContext'
import {useAddressProvider} from '../../context/addressContext'
import axios from 'axios'
import toast from 'react-hot-toast';
import { useSelector } from 'react-redux'
import Overview from './component/overview'
import Positions  from './component/poisitions'
import OpenOrder from './component/order'

const API = "https://api.coingecko.com/api/v3/simple/price?ids=aptos%2Cbitcoin%2Cethereum&vs_currencies=usd&include_market_cap=false&include_24hr_vol=false&include_24hr_change=true&include_last_updated_at=false&precision=2";

function Portfolio({theme, setTheme}) {
  const account = useSelector((state) => state.account)

  const [activeComponent, setActiveComponent] = useState('overview');
  const {isConnected, setIsConnected} = useWalletProvider()
  const {address, setAddress} = useAddressProvider()
  const [tokenprices, setTokenprices] = useState([]);

  const apiUrl = 'http://localhost:8081/api/';

  const fetchUsers = async (url) => {
    try {
      const res = await fetch(url);
      const data = await res.json();
      if (data) {
        setTokenprices(data);
      }
    } catch (e) {
      console.error(e);
    }
  };


  React.useEffect(() => {
    const fetchData = async () => {
      await fetchUsers(API);
    };
    fetchData();
  }, []);

  const traddata = [
    {
      name: "Bitcoin",
      icon: btc,
      value: tokenprices.bitcoin ? tokenprices.bitcoin.usd : 0,
      change: tokenprices.bitcoin ? tokenprices.bitcoin.usd_24h_change : 0,
    },
    {
      name: "Ethereum",
      icon: eth,
      value: tokenprices.ethereum ? tokenprices.ethereum.usd : 0,
      change: tokenprices.ethereum ? tokenprices.ethereum.usd_24h_change : 0,
    },
    {
      name: "Aptos",
      icon: apt,
      value: tokenprices.aptos ? tokenprices.aptos.usd : 0,
      change: tokenprices.aptos ? tokenprices.aptos.usd_24h_change : 0,
    },
  ]; 
  const deposit = async () => {
    const req = {
      jsonrpc: "2.0",
      id: 1,
      method: "private/deposit",
      params :{
        from: address,
        currency: "USDC",
        amount: 1000
      }
    }
    const resp = axios.post(apiUrl, req )
    toast.promise(resp, {
      loading: 'Adding Funds',
      success: 'Deposited $1000. Enjoy trading!',
      error: 'Some error occured',
    });
    
  }
  const withdraw = async () => {
    const tx = {
      type: "entry_function_payload",
      function: "0x3f4111e71d011986d24815ce66ce35900c892561d8cf163c41af23100b7d55a7::faucet::mint",
      arguments: [1000000],
      type_arguments: ["0x3f4111e71d011986d24815ce66ce35900c892561d8cf163c41af23100b7d55a7::usdc::USDC"]
    }
    try {
      await window.aptos.signAndSubmitTransaction(tx);

    } catch{
      console.log("cancelled")
    } 
  }

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
    <Layout theme={theme} setTheme={setTheme}>
      <div className={style.layoutbody}>
        <div className={style.layoutcard}>
          <PBlocks bwidth="20vw" bheight="95%">
            <div className={style.sidelink}>
              <Sidebarbutton
                img={<Globe size={15} />}
                text="Overview"
                active={activeComponent === "overview"}
                onClick={() => setActiveComponent("overview")}
              />
              <Sidebarbutton
                img={<Layers size={15} />}
                text="Positions"
                active={activeComponent === "positions"}
                onClick={() => setActiveComponent("positions")}
              />
              <Sidebarbutton
                img={<AlignLeft size={15} />}
                text="Open Orders"
                active={activeComponent === "openOrders"}
                onClick={() => setActiveComponent("openOrders")}
              />
              <Sidebarbutton
                img={<History size={15} />}
                text="Order History"
                active={activeComponent === "orderHistory"}
                onClick={() => setActiveComponent("orderHistory")}
              />
            </div>
            {!isConnected ? 
              <div style={{cursor:'pointer', color:'white'}} className={style.sideconnect} onClick={handleConnectWallet}>
                Connect Wallet
              </div>
                : 
                <div className={style.sideconnected_div}>
                <div style={{cursor:'pointer'}} onClick={deposit} className={style.sideconnected}>Faucet</div>
                <div style={{cursor:'pointer'}} onClick={withdraw} className={style.sideconnected}>Withdraw</div>
                </div>
            }
        </PBlocks>
      </div>
      <div className={style.layoutcard}>
        <PBlocks bwidth='58vw' bheight='95%'>
          {activeComponent === 'overview' && <Overview/>}
          {activeComponent === 'positions' && <Positions/>}
          {activeComponent === 'openOrders' && <OpenOrder/>}
          {activeComponent === 'orderHistory' && <OrderHistory/>}
        </PBlocks>
      </div>
      <div className={style.layoutcard}>
        <PBlocks bwidth='20vw' bheight='95%'>
          <h5>Current MarketCap</h5>
          {traddata.map((data, index) => (
            <TradData key={index} {...data} />
          ))}
        </PBlocks>
      </div>
    </div>
  </Layout>
  )
}
export default Portfolio;

function Sidebarbutton({ img, text, active, onClick }) {
  return (
    <div
      className={`${style.sidebutton} ${
        active ? style.sidebarbuttonactive : ""
      }`}
      onClick={onClick}
    >
      <div className={style.sidebuttonicon}>{img}</div>
      <div className={style.sidebuttontext}>{text}</div>
    </div>
  );
}

function TradData({ name, icon, value, change }) {
  let tcolor;
  let bcolor;
  if (change > 0) {
    tcolor = "rgba(0,255,0)";
    bcolor = "rgba(0,255,0,0.1)";
  } else if (change < 0) {
    tcolor = "rgba(255,0,0)";
    bcolor = "rgba(255,0,0,0.1)";
  }


  return (
    <div className={style.traddata} style={{ backgroundColor: bcolor }}>
      <div className={style.traddatacontent}>
        <div className={style.traddataicon}>
          <img src={icon} alt="trad data icon" />
        </div>
        <div className={style.traddatacontentname}>{name}</div>
      </div>
      <div className={style.traddatanums}>
        <div className={style.traddatavalue}> &#36;{value}</div>
        <div className={style.traddatachange} style={{ color: tcolor }}>
          {change.toFixed(2)}%
        </div>
      </div>
    </div>
  );
}

function OrderHistory() {
  const [activeTab, setActiveTab] = useState('allPositions');

  return (
    <div className={style.orderhistory}>
      <h4>Order History</h4>
    </div>
  );
}
