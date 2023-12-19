import React, { useEffect, useState } from "react";
import style from "./style.module.css";
import { NavLink } from "react-router-dom";
import { ReactComponent as Sun } from "../assets/Sun.svg";
import { ReactComponent as Moon } from "../assets/Moon.svg";
import logo from "../assets/logo.svg";
import { useWalletProvider } from "../context/walletContext";
import { useAddressProvider } from "../context/addressContext";
import { useAppDispatch } from "../redux/hooks";
import { useAppSelector } from "../redux/hooks";
import {
  setColl,
  setDeposits,
  setOrders,
  setPosition,
  setTrades,
  setWithdrawals,
  setAvailableMargin
} from "../redux/features/accountSlice";

function TNavbar({ theme, setTheme }) {
  const { isConnected, setIsConnected } = useWalletProvider();
  const { address, setAddress } = useAddressProvider();
  const dispatch = useAppDispatch();
  const account = useAppSelector((state) => state.accountSlice);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 900);
  const [availableMargin, setAvailableMargin] = useState(0.0);
  const [pl, setPL] = useState(0.0);
  const [equity, setEquity] = useState(0.0);



  const setDarkMode = () => {
    document.querySelector("body").setAttribute("data-theme", "light");
  };

  const setLightMode = () => {
    document.querySelector("body").setAttribute("data-theme", "dark");
  };

  const toggleTheme = (e) => {
    if (e.target.checked) {
      const Theme = theme === "dark" ? "light" : "dark";
      setTheme(Theme);
      setDarkMode();
    } else {
      const Theme = theme === "light" ? "dark" : "light";
      setTheme(Theme);
      setLightMode();
    }
  };

  useEffect(() => {
    const init = async () => {
      const ws = new WebSocket(`ws://127.0.0.1:8082/account/${address}`);
      ws.onopen = () => {
        ws.onmessage = (msg) => {
          const resp = JSON.parse(msg.data).response;

          // console.log('Received WebSocket data:', resp);


          setEquity(resp.collateral)

          // Extract margin data for a specific position (BTC-20DEC23 in this example)
          const btcMargin = resp.positions["BTC-20DEC23"].margin || 0;
          const ethMargin = resp.positions["ETH-20DEC23"].margin || 0;
          const aptMargin = resp.positions["APT-20DEC23"].margin || 0;
          const totalMargin = btcMargin + ethMargin + aptMargin;
          const availabe = resp.collateral - totalMargin;
          setAvailableMargin(availabe)

          // Calculate and update "P&L" and "Equity"
          const btcUnrealizedPnl = resp.positions["BTC-20DEC23"].unrealized_pnl || 0;
          const ethUnrealizedPnl = resp.positions["ETH-20DEC23"].unrealized_pnl || 0;
          const aptUnrealizedPnl = resp.positions["APT-20DEC23"].unrealized_pnl || 0;
          const totalUnrealizedPnl = btcUnrealizedPnl + ethUnrealizedPnl + aptUnrealizedPnl;
          setPL(totalUnrealizedPnl)

          dispatch(setColl(resp.collateral));
          dispatch(setDeposits(resp.deposits));
          dispatch(setOrders(resp.open_orders));
          dispatch(setPosition(resp.positions));
          dispatch(setTrades(resp.trades));
          dispatch(setWithdrawals(resp.withdrawals));
          // console.log(resp.available_margin)
          // dispatch(setAvailableMargin(resp.withdrawals));
        };
      };
    };
    if (isConnected) {
      init();
    }
  }, [isConnected, equity]);

  // React.useEffect(() => {}, [account.collateral])


  const handleConnectWallet = async () => {
    // Function to check if Petra is installed
    const getAptosWallet = () => {
      if ("aptos" in window) {
        return window.aptos;
      } else {
        window.open("https://petra.app/", "_blank");
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
      alert("Failed to connect to Petra. Please try again.");
    }
  };

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 900);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [theme, setTheme]);

  return (
    <>
      {isMobile ? (
        <div className={style.tnav} style={{height: "10%"}}>
        <div className={style.navlink1}>
            <div className={style.logo}>
              <img src={logo} alt="logo" />
            </div>
            <div className={style.navlink3}>
              <NavLink
                to="/trading"
                exact
                style={({ isActive }) =>
                  isActive ? { color: "rgb(76, 215, 244)" } : {}
                }
              >
                Trading
              </NavLink>
              <NavLink
                to="/portfolio"
                exact
                style={({ isActive }) =>
                  isActive ? { color: "rgb(76, 215, 244)" } : {}
                }
              >
                Portfolio
              </NavLink>
            </div>
          </div>
        </div>
      ) : (
        <div className={style.tnav}>
          <div className={style.navlink1}>
            <div className={style.logo}>
              <img src={logo} alt="logo" />
            </div>
            <div className={style.navlink3}>
              <NavLink
                to="/trading"
                exact
                style={({ isActive }) =>
                  isActive ? { color: "rgb(76, 215, 244)" } : {}
                }
              >
                Trading
              </NavLink>
              <NavLink
                to="/portfolio"
                exact
                style={({ isActive }) =>
                  isActive ? { color: "rgb(76, 215, 244)" } : {}
                }
              >
                Portfolio
              </NavLink>
            </div>
          </div>
          <div className={style.navlink2}>
            <div className={style.navnums}>
            <NavNum label='Available Margin' value={typeof availableMargin === 'number' ? availableMargin : 'N/A'} />
            <NavNum label='P&L' value={typeof pl === 'number' ? pl : 'N/A'} />
            <NavNum label='Equity' value={typeof equity === 'number' ? equity  : 'N/A'} />
            </div>
            {isConnected ? (
              <div className={style.connected} style={{ fontSize: "13px" }}>
                {address.slice(0, 6)}....{address.slice(-4)}
              </div>
            ) : (
              <div
                className={style.connect}
                style={{ cursor: "pointer" }}
                onClick={handleConnectWallet}
              >
                Connect Wallet
              </div>
            )}
            <div className={style.dark_mode}>
              <input
                className={style.dark_mode_input}
                type="checkbox"
                id="darkmode-toggle"
                onChange={toggleTheme}
              />
              <label
                className={style.dark_mode_label}
                htmlFor="darkmode-toggle"
              >
                <div className={style.sun}>
                  <Moon />
                </div>
                <div className={style.Moon}>
                  <Sun />
                </div>
              </label>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default TNavbar;

function NavNum({ label, value }) {

  useEffect(() => {}, [value])

  const formattedValue = typeof value === 'number' ? value.toFixed(2) : 'N/A';


  return (
    <div className={style.navnum}>
      <div className={style.head}>{label}</div>
      <div className={style.value}>${formattedValue}</div>
    </div>
  );
}
