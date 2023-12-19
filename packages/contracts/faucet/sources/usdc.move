module exchange_faucet::usdc {
    use aptos_std::string;
    use exchange_faucet::faucet;

    struct USDC {}

    const NAME: vector<u8> = b"USD coin";
    const SYMBOL: vector<u8> = b"USDC";
    const DECIMALS: u8 = 6;
    const MONITOR_SUPPLY: bool = false;

    fun init_module(account: &signer) {
        faucet::initialize<USDC>(
            account,
            string::utf8(NAME),
            string::utf8(SYMBOL),
            DECIMALS,
            MONITOR_SUPPLY
        );
    }

    #[test(owner = @exchange_faucet)]
    public fun init_coin_for_test(owner: &signer){
        init_module(owner);
    }

}