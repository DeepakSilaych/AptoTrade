import {configureStore} from '@reduxjs/toolkit';
import {setupListeners} from '@reduxjs/toolkit/query';
import priceSlice from './features/priceSlice'
import accountSlice from './features/accountSlice';

export const store = configureStore({
    reducer: {
        price: priceSlice,
        account: accountSlice
    },
});


setupListeners(store.dispatch);

