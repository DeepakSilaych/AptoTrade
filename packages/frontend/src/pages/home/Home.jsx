import React, {useEffect, useState} from 'react'
import UserData from './Userdata';
import style from './home.module.css'
import { Link } from 'react-router-dom'
// import Video from "../../assets/check.mp4";
import Image from "../../assets/trading_main.png"
import {Github, Facebook, Linkedin} from 'lucide-react'
import logo from '../../assets/logo.svg'

const API = "https://api.coingecko.com/api/v3/simple/price?ids=aptos%2Cbitcoin%2Cethereum&vs_currencies=usd&include_market_cap=false&include_24hr_vol=false&include_24hr_change=true&include_last_updated_at=false&precision=2";

function Home() {
    const [users, setUsers] = useState([]);
    const [windowWidth, setWindowWidth] = useState(window.innerWidth);

    const fetchUsers = async (url)=>{
        try{
            const res = await fetch(url);
            const data = await res.json();
            if(data.length >0){
                setUsers(data);
            }
            setUsers(data)
        }catch(e){
            console.error(e);
            
        }
    }
    useEffect(() => {
        fetchUsers(API);

        const handleResize = () => {
            setWindowWidth(window.innerWidth);
        };

        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);


  return (

    <div className={style.bg}>
        <div className={style.navbar}>
            <div className={style.nav_logo}>
                <p className={style.nav_text}>AptoTrade</p>
            </div>
            <div>
                <Link to='docs' className={style.docs_button}>Docs &#8599;</Link>
                <Link to='status' className={style.docs_button}>Status &#8599;</Link>
            </div>
            <Link to='trading' className={style.nav_button}>
            <div className={style.button}>Trade Now</div>
            </Link>
        </div>
        <div className={style.herosection}>
            <div className={style.hero_text}>
                <p>Move Fast, Stay Ahead<br/>
                    Trade Smart.<br/>
                    All on <b>AptoTrade</b>.
                </p>
            </div>
        </div>
        <div className= {style.information}>
            <div className={style.inside}>
                <div className={style.inside_a}>
                    <UserData users = {users}/>
                </div>

            </div>
        </div>

        <div className={style.hero_img_section}>
            <div className={style.hero_img}>  
            </div>
            <div className={style.hero_img_text}>
                <img className={style.round} src={Image} alt='logo' />
                <h3>Getting Started</h3>
                <p>We are excited that you are here, and we look forward to getting to know you. Welcome to the AptoTrade community!</p>
            </div>
        </div>

        <div className={style.decen_section}>
            <div className={style.decen_text}>
            {windowWidth > 470 ? (
                <p>Decentralised Trading <br/>     
                    With Centralized <br/>
                    Exchange Efficiency</p>
                ) : (
                    <p>Decentralised Trading With Exchange Efficiency</p>
                    )}
            </div>
            <div className={style.decen_information}>
                <p>Aptos supports expirable futures, and many other products within a single margin account. Combining off-chain margining with on-chain settlement, the platform allows traders to have unparalleled performance and latency while inheriting the security of the Aptos blockchain. </p>
                <div className={style.decen_number}>
                <div className={style.decen_trade}>
                    <div>
                    <p className={style.total}>Total volume Traded</p>
                    <p className={style.decen_numberfont}>{'>'}$173.68M</p>
                    </div>
                    <div className={style.total_margin}>
                    <p className={style.total}>Aptos Tanscation Exchange</p>
                    <p className={style.decen_numberfont}>{'>'}130,000tps</p>
                    </div>
                </div>
                <div className={style.decen_trade}>
                    <div>
                    <p className={style.total}>Current Market Cap</p>
                    <p className={style.decen_numberfont}>{'>'}$2.17B</p>
                    </div>
                    
                    <div className={style.total_m}>
                    <p className={style.total}> APT Market Cap</p>
                    <p className={style.decen_numberfont}>{'>'}$8.29B</p>
                    </div>
                </div>
            </div>
            </div>
        </div>

        
        <h2 className={style.h2}>Why WE?</h2>
        <div className={style.whatwedo}>
            <div>
                We provide a non-custodial trading environment where users have full control and ownership of their assets
            </div>
            <div>
                We ensure instant settlement of all trades, profits, and losses via smart contracts upon the expiry of 24-hour contracts
            </div>
            <div>
                We offer a variety of futures contracts along with real-time market data and automated risk mitigation features.
            </div>
        </div>


        <div className={style.footer}>
            <div className={style.footerlogo}>
                <img src={logo} alt="AptoTrade logo" />
            </div>
            <div className={style.footer_information}>
                <p className={style.foot_info_text}>Make Your<br/> Move</p>
            </div>
            <div className={style.footer_link}>
                <div className={style.link_inside}>
                    <h4>Pages</h4>
                    <Link to={"/trade/apt"}>Trade</Link>
                    <Link to={"/portfolio"}>Portfolio</Link>
                    <Link to={"/docs"}>Docs</Link>
                </div>
                <div className={style.link_inside}>
                    <h4>Built on</h4>
                    <a href="https://aptos.dev/move/book/summary/">Aptos</a>
                    <a href="https://aptos.dev/move/book/summary/">Move</a>
                    <a href="https://www.econialabs.com/">Econia</a>
                </div>
            </div>   
            <div className={style.footer_end}>
            <div className={style.link_inside_icons}>   
                    <h4>Follow Us</h4>
                    <div>
                        <a href="https://www.linkedin.com/company/aptoslabs/"><Linkedin /></a>
                        <a href="https://m.facebook.com/people/Aptos-Network/100088584127971/"><Facebook /></a>
                        <a url="https://github.com/aptos-labs"><Github/></a>
                    </div>
                </div>
            </div>   
        </div>
        <div className={style.footer_end}>
                <p>© 2023 AptoTrade rights reserved</p>
        </div>
    </div>
  )
}

export default Home;