import uuid
import os
from supabase import create_client, Client
from exchange.utils import get_logger

logger = get_logger()

data = {
   "USDC":{
        'id': 6, 
        'created_at': '2023-01-03T18:28:59.981053+00:00', 
        'name': 'Circle USD', 
        'symbol': 'USDC', 
        'precision': 6, 
        'ctype': 'ERC20', 
        'is_coll_asset': True, 
        'withdrawal_fee': 0, 
        'portfolio_margin_params': None, 
        'standard_margin_params': None, 
        'pyth_mainnet_price_key': 'Gnt27xtC473ZT2Mw5u8wZ68Z3gULkSTb5DuxJy7eJotD', 
        'updated_at': '2023-01-03T18:28:59.981053+00:00', 
        'address': None
    },
    "BTC":{
        'id': 9, 
        'created_at': '2023-01-03T18:35:08.727489+00:00', 
        'name': 'Bitcoin', 
        'symbol': 'BTC', 
        'precision': 8, 
        'ctype': 'ERC20', 
        'is_coll_asset': False, 
        'withdrawal_fee': 0, 
        'portfolio_margin_params': {'atm_range': 0.1, 'price_range': 15, 'risk_free_rate': 0, 'perp_contingency': 0.006, 'volatility_range_up': 45, 'volatility_range_down': 30, 'option_sum_contingency': 0.01, 'futures_orders_im_factor': 0.0309}, 
        'standard_margin_params': {'min_im_perc': 2, 'min_mm_perc': 1, 'scaling_perc': 0.005}, 
        'pyth_mainnet_price_key': 'GVXRSBjFk6e6J3NbVPXohDJetcTjaeeuykUpbQF8UoMU', 
        'updated_at': '2023-01-03T18:35:08.727489+00:00', 
        'address': None
    },
    "ETH": {
        'id': 8, 
        'created_at': '2023-01-03T18:32:34.675972+00:00', 
        'name': 'Ethereum', 
        'symbol': 'ETH', 
        'precision': 18, 
        'ctype': 'ERC20', 
        'is_coll_asset': False, 
        'withdrawal_fee': 0, 
        'portfolio_margin_params': {'atm_range': 0.1, 'price_range': 15, 'risk_free_rate': 1e-05, 'perp_contingency': 0.009, 'volatility_range_up': 38, 'volatility_range_down': 24, 'option_sum_contingency': 0.01, 'futures_orders_im_factor': 0.0309}, 
        'standard_margin_params': {'min_im_perc': 2, 'min_mm_perc': 1, 'scaling_perc': 0.0004}, 
        'pyth_mainnet_price_key': 'JBu1AL4obBcCMqKBBxhpWCNUt136ijcuMZLFvTP7iWdB', 
        'updated_at': '2023-01-03T18:32:34.675972+00:00', 
        'address': None
    },
    "APT": {
        'id': 7, 
        'created_at': '2023-01-03T18:32:34.675972+00:00', 
        'name': 'Aptos', 
        'symbol': 'APT', 
        'precision': 18, 
        'ctype': 'ERC20', 
        'is_coll_asset': False, 
        'withdrawal_fee': 0, 
        'portfolio_margin_params': {'atm_range': 0.1, 'price_range': 15, 'risk_free_rate': 1e-05, 'perp_contingency': 0.009, 'volatility_range_up': 38, 'volatility_range_down': 24, 'option_sum_contingency': 0.01, 'futures_orders_im_factor': 0.0309}, 
        'standard_margin_params': {'min_im_perc': 2, 'min_mm_perc': 1, 'scaling_perc': 0.0004}, 
        'pyth_mainnet_price_key': 'JBu1AL4obBcCMqKBBxhpWCNUt136ijcuMZLFvTP7iWdB', 
        'updated_at': '2023-01-03T18:32:34.675972+00:00', 
        'address': None
    }
}



# url: str = os.environ.get("SUPABASE_URL", "https://kkkbjpsuvgsnosmkcmxh.supabase.co")
# # key: str = os.environ.get("SUPABASE_KEY")
# key: str = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtra2JqcHN1dmdzbm9zbWtjbXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzI3NDAyNjksImV4cCI6MTk4ODMxNjI2OX0.IdDnM502eYGcU4OAt_HZwj1xkEKVngfCR1lk5-8MTGo")

# supabase: Client = create_client(url, key)

class Currency:
    def __init__(self, symbol) -> None:
        # data = supabase.table("currencies").select("*").eq("symbol", symbol).execute()
        raw_currency_data = data[symbol]
        # print(raw_currency_data)
        self.id = raw_currency_data["id"]
        self.name = raw_currency_data["name"]
        self.symbol = raw_currency_data["symbol"]
        self.precision = raw_currency_data["precision"]
        self.ctype = raw_currency_data["ctype"]
        self.is_coll_asset = raw_currency_data["is_coll_asset"]
        self.withdrawal_fee = raw_currency_data["withdrawal_fee"]
        self.portfolio_margin_params = raw_currency_data["portfolio_margin_params"]
        self.standard_margin_params = raw_currency_data["standard_margin_params"]
        self.pyth_mainnet_price_key = raw_currency_data["pyth_mainnet_price_key"]
        self.created_at = raw_currency_data["created_at"]
        self.updated_at = raw_currency_data["updated_at"]
        self.address = raw_currency_data["address"] if raw_currency_data["address"] is not None else "0x"
        # print(self.portfolio_margin_params)
        # print(self.portfolio_margin_params["risk_free_rate"])
        self.price = None

    def get_spot_price(self):
        return self.price

    def get_data(self):
        return {
            "name": self.name,
            "symbol": self.symbol,
            "address": self.address,
            "precision": self.precision,
            "ctype": self.ctype,
            "is_coll_asset": self.is_coll_asset,
            "withdrawal_fee": self.withdrawal_fee,
            "standard_margin_params": self.standard_margin_params,
            "portfolio_margin_params": self.portfolio_margin_params
        }

    # def set_collateral(self):
    #     self.is_coll_asset = True
    #     data = supabase.table("currencies").select("*").eq("symbol", "USDT").execute()
    #     assert len(data.data) == 1
    #     raw_currency_data = data.data
    #     assert raw_currency_data["address"] is not None
    #     self.address = raw_currency_data["address"]