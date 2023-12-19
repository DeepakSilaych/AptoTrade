/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { createContext, useContext, useState } from 'react';


const AddressContext = createContext ({
	address: false,
	setAddress: () => null, 
});

export const AddressContextProvider = ({children}) => {
	const [address, setAddress] = useState(false);
	return (
		<AddressContext.Provider value={{address, setAddress}}>
			{children}
		</AddressContext.Provider>
	);
};

export const useAddressProvider = () => useContext(AddressContext); 