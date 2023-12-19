module exchange_faucet::apt {
    use aptos_std::string;
    use exchange_faucet::faucet;

    struct APT {}

    const NAME: vector<u8> = b"Apt";
    const SYMBOL: vector<u8> = b"APT";
    const DECIMALS: u8 = 6;
    const MONITOR_SUPPLY: bool = false;

    fun init_module(account: &signer) {
        faucet::initialize<APT>(
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