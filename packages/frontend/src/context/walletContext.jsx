/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { createContext, useContext, useState } from 'react';


const WalletContext = createContext ({
	isConnected: false,
	setIsConnected: () => null, 
});

export const WalletContextProvider = ({children}) => {
	const [isConnected, setIsConnected] = useState(false);
	return (
		<WalletContext.Provider value={{isConnected, setIsConnected}}>
			{children}
		</WalletContext.Provider>
	);
};

export const useWalletProvider = () => useContext(WalletContext); 