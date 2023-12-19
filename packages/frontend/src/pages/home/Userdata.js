import React from "react";
import style from "./home.module.css"

const UserData = ({ users }) => {
    const userEntries = Object.entries(users).map(([coin, data]) => ({
        coin,
        price: data.usd,
        inc: data.usd_24h_change,
    }));


    const formatinc = (inc) => {
        const formattedinc = inc.toFixed(2); 
        if (inc > 0) {
            return "+" + formattedinc + "%";
        }
        return formattedinc + "%"; 
    };

    return (
        <div className={style.userdata}>
            {userEntries.map((curUser, index) => (
                <div key={index} className={style.user_data_ow}>
                    <div className={style.data_cell}>{curUser.coin.toUpperCase()}</div>
                    <div className={style.data_cell_price}>${curUser.price}</div>
                    <div className={style.data_cell}
                    style = {{color: curUser.inc < 0 ? 'red' : '#03C105'}}>{formatinc(curUser.inc)}</div>
                </div>
            ))}
        </div>
    );
}

export default UserData;
