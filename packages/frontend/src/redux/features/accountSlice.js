import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    positions: {},
	collateral: 0,
	open_orders: {},
	deposits: {},
	withdrawals: {},
	trades: {},
	available_margin: 0
};

export const account = createSlice({
	name: 'account',
	initialState,
	reducers: {
		reset: () => initialState,
		setPosition: (state, action) => {
			state.positions = action.payload;
		},
		setColl: (state, action) => {
			state.collateral = action.payload;
		},
		setOrders: (state, action) => {
			state.open_orders = action.payload;
		},
		setDeposits: (state, action) => {
			state.deposits = action.payload;
		},
		setWithdrawals: (state, action) => {
			state.withdrawals = action.payload;
		},
		setTrades: (state, action) => {
			state.trades = action.payload;
		},
		setAvailableMargin: (state, action) => {
			state.available_margin = action.payload;
		},
	},
});

export const { reset, setColl, setDeposits, setOrders, setPosition, setTrades, setWithdrawals, setAvailableMargin } = account.actions;
export default account.reducer;