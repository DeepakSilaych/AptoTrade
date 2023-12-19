PROFILE=local
ACCOUNT=local
FAUCET_URL=http://0.0.0.0:8081
REST_URL=http://0.0.0.0:8080

# env
local_testnet:
	aptos node run-local-testnet --with-faucet --force-restart

init_profiles:
	aptos init --profile AptEconia --network devnet
	aptos init --profile AptFaucet --network devnet
	aptos init --profile AptManager --network devnet
	aptos init --profile aptUser1 --network devnet
	aptos init --profile aptUser2 --network devnet

set_env:
	testUser1=0x95963aef9fdc8f34538e2285a4711b458d493b550ef6877991ab5613e2d84771
	testUser2=0xe1737975c9103be4107e71e611032805ef61aa6fa33d38794b6b3038b383c9a7
	faucet=0x71c55932c638ad8ec8607f55cdc81ef4ba13e7f920524d7f2193ed9db77320bd
	econia=0xcac06482852f65b5ca07b5b3fdc623750f0535dbe44dfb0b28e7adc492aff99b
	manager=0x9b0ab538f63666b4901f6bfbe587213e06979ce761342d6025f0d1ce193bab4b

fund:
	aptos account fund-with-faucet --profile ${PROFILE} --account econia --amount 99999999
	aptos account fund-with-faucet --profile ${PROFILE} --account faucet --amount 99999999
	aptos account fund-with-faucet --profile ${PROFILE} --account manager --amount 99999999
	aptos account fund-with-faucet --profile ${PROFILE} --account testUser1 --amount 99999999
	aptos account fund-with-faucet --profile ${PROFILE} --account testUser2 --amount 99999999

compile_econia:
	aptos move compile --package-dir econia --named-addresses econia=AptEconia  --skip-attribute-checks

deploy_econia:
	aptos move publish --package-dir econia --named-addresses econia=AptEconia --included-artifacts none --profile AptEconia --skip-attribute-checks

compile_faucet:
	aptos move compile --package-dir faucet --named-addresses exchange_faucet=AptosTradeFaucet,econia=AptosTradeEconia --skip-attribute-checks

deploy_faucet:
	aptos move publish --package-dir faucet --named-addresses exchange_faucet=AptFaucet,econia=AptEconia --included-artifacts none --profile AptFaucet --skip-attribute-checks

test_faucet:
	aptos move test --package-dir faucet --named-addresses exchange_faucet=AptosTradeFaucet,econia=AptosTradeEconia --skip-attribute-checks


compile_manager:
	aptos move compile --package-dir manager --named-addresses exchange_faucet=AptosTradeFaucet,econia=AptosTradeEconia,manager=AptosTradeManager --skip-attribute-checks

test_manager:
	aptos move test --package-dir manager --named-addresses exchange_faucet=faucet,econia=econia,manager=manager --skip-attribute-checks

deploy_manager:
	aptos move publish --package-dir manager --named-addresses exchange_faucet=AptFaucet,econia=AptEconia,manager=AptManager --included-artifacts none --profile AptManager --skip-attribute-checks
