module manager::manager {
    use aptos_std::coin;
    use econia::market;
    use econia::user::{
        deposit_from_coinstore,
        get_market_account_id,
        has_market_account_by_market_account_id,
        register_market_account,
        withdraw_to_coinstore,
    };
    use std::signer::{address_of};
    use exchange_faucet::faucet::mint;

    const BID: bool = false;
    const BUY: bool = false;
    /// Flag to cancel maker and taker order during a self match.
    const CANCEL_BOTH: u8 = 1;
    /// Flag to cancel maker order only during a self match.
    const CANCEL_MAKER: u8 = 2;
    /// Flag to cancel taker order only during a self match.
    const CANCEL_TAKER: u8 = 3;
    const NO_CUSTODIAN: u64 = 0;
    const SHIFT_MARKET_ID: u8 = 64;
    const NO_RESTRICTION: u8 = 0;



    fun before_order_placement<
        BaseType,
        QuoteType
    >(
        user: &signer,
        deposit_amount: u64,
        market_id: u64,
        side: bool,
    ) {
        let user_addr = address_of(user);
        // Create MarketAccount if not exists
        // Least significant 64 bits is 0 because we use NO_CUSTODIAN
        let user_market_account_id = get_market_account_id(
            market_id,
            NO_CUSTODIAN,
        );
        if (!has_market_account_by_market_account_id(
            user_addr,
            user_market_account_id
        )) {
            register_market_account<BaseType, QuoteType>(
                user,
                market_id,
                NO_CUSTODIAN
            );
        };
        // Deposit `deposit_amount` into the MarketAccount
        if (side == BID) {
            // mint coins
            mint<QuoteType>(user, deposit_amount);
            deposit_from_coinstore<QuoteType>(
                user,
                market_id,
                NO_CUSTODIAN,
                deposit_amount // size * price * tick_size
            );
            // Register the BaseType if it is not registered
            if (!coin::is_account_registered<BaseType>(user_addr)) {
                coin::register<BaseType>(user);
            };
        } else {
            mint<BaseType>(user, deposit_amount);
            deposit_from_coinstore<BaseType>(
                user,
                market_id,
                NO_CUSTODIAN,
                deposit_amount // size * lot_size
            );
            // Register the QuoteType if it is not registered
            if (!coin::is_account_registered<QuoteType>(user_addr)) {
                coin::register<QuoteType>(user);
            };
        };
    }


    /// Convenience script for `market::place_limit_order_user()`.
    ///
    /// This script will create a user MarketAccount if it does not already
    /// exist and will withdraw from the user's CoinStore to ensure there is
    /// sufficient balance to place the Order.
    public entry fun place_limit_order_user_entry<
        BaseType,
        QuoteType
    >(
        user: &signer,
        deposit_amount: u64,
        market_id: u64,
        integrator: address,
        side: bool,
        size: u64,
        price: u64,
    ) {
        before_order_placement<BaseType, QuoteType>(
            user,
            deposit_amount,
            market_id,
            side,
        );
        // Place the order
        market::place_limit_order_user_entry<BaseType, QuoteType>(
            user,
            market_id,
            integrator,
            side,
            size,
            price,
            NO_RESTRICTION,
            CANCEL_MAKER,
        );
    }

    #[cmd]
    /// Convenience script for `market::place_market_order_user()`.
    ///
    /// This script will create a user MarketAccount if it does not already
    /// exist and will withdraw from the user's CoinStore to ensure there is
    /// sufficient balance to place the Order.
    public entry fun place_market_order_user_entry<
        BaseType,
        QuoteType
    >(
        user: &signer,
        deposit_amount: u64,
        market_id: u64,
        integrator: address,
        direction: bool,
    ) {
        before_order_placement<BaseType, QuoteType>(
            user,
            deposit_amount,
            market_id,
            direction, // side == direction
        );
        // Place the order
        let (base_traded, quote_traded, _) =
            market::place_market_order_user<BaseType, QuoteType>(
                user,
                market_id,
                integrator,
                direction,
                deposit_amount,
                CANCEL_MAKER,
            );
        if (direction == BUY) {
            // Return the unused quote
            withdraw_to_coinstore<BaseType>(
                user,
                market_id,
                base_traded,
            );
        } else {
            // Return the unused base
            withdraw_to_coinstore<QuoteType>(
                user,
                market_id,
                quote_traded,
            );
        };
    }



}
