import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    Price: '0',
};

export const price = createSlice({
	name: 'price',
	initialState,
	reducers: {
		reset: () => initialState,
		setPrice: (state, action) => {
			state.Price = action.payload;
		},
	},
});

export const { reset, setPrice } = price.actions;
export default price.reducer;