import React from 'react';
import {
  PontemWalletAdapter,
  WalletProvider as BaseWalletProvider,
} from '@manahippo/aptos-wallet-adapter';

const WalletProvider = ({ children }) => {
  const wallets = [
    new PontemWalletAdapter(),
    // add other wallet adapters here if needed
  ];

  return (
    <BaseWalletProvider
      wallets={wallets}
      onError={(error) => console.log('Wallet Error:', error)}
    >
      {children}
    </BaseWalletProvider>
  );
};

export default WalletProvider;
