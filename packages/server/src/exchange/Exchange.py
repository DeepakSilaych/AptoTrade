import asyncio

from exchange.producer import get_redpanda_producer
from exchange.markets.Instrument import InstrumentCode
from exchange.utils import get_logger
from exchange.markets.Index import Index
from exchange.matchingengine.Order import LimitOrder,MarketOrder,Side,CancelOrder
from exchange.riskengine.margin_engine import calculate_total_margin_required
import time
from threading import Thread
from uuid import uuid1
from collections import defaultdict


logger = get_logger()

class Exchange:
    def __init__(self, tradable_assets=[], currencies=[], indices=[], instruments=[]):
        self.producer = get_redpanda_producer()
        self.tradable_assets = tradable_assets
        self.currencies = currencies
        self.indices = indices
        self.instruments = instruments

        self.price_feed = {}

        self.supported_colls = [
            currency for currency in self.currencies if currency.is_coll_asset
        ]

        # currencies that are tradable and support portfolio margin
        self.tradable_asset_symbols = [
            currency.symbol for currency in self.tradable_assets
        ]

        # symbol of currencies supported as collateral
        self.supported_coll_symbols = [
            currency.symbol for currency in self.currencies if currency.is_coll_asset
        ]

        # name of supported indices
        self.supported_indices = [index.name for index in self.indices]

        # name of supported instruments
        self.supported_instrument_names = [
            instrument.name for instrument in self.instruments
        ]

        # mapping: instrument name => insturment code
        self.instrument_codes = {}
        for instrument in self.instruments:
            self.instrument_codes[instrument.name] = instrument.code

        # mapping: instrument name => insturment index in self.instrument
        self._instrument_idxs = {}
        for idx in range(len(self.instruments)):
            self._instrument_idxs[self.instruments[idx].name] = idx

        # mapping: index name => "index" index in self.indices
        self._index_idxs = {}
        for idx in range(len(self.indices)):
            self._index_idxs[self.indices[idx].name] = idx

        self.supported_dated_futures = [
            instrument.name
            for instrument in self.instruments
            if instrument.code == InstrumentCode.USD_M_FUTURE
        ]

        self.msgs = []

        # mapping: instrument name => coressponding trades
        self.trades = {k: [] for k in self.supported_instrument_names}
        self.tickers = {k: None for k in self.supported_instrument_names}
        self.expired_contracts = []
        self.accounts = {}
        # self.sub_accounts = {}
        self.users = []
        self.api_keys = {}
        self.stats = {
            "supported_currencies": len(self.currencies),
            "supported_collateral": len(self.supported_coll_symbols),
            "supported_indices": len(self.indices),
            "active_instruments": len(self.instruments),
            "expired_instruments": len(self.expired_contracts),
            "users_count": len(self.users),
        }

        # all indices have a copy of the entire price feed object
        for index in self.indices:
            index.set_price_feed(self.price_feed)


        # ------------------------- Start Threads --------------------------
        for instrument in self.instruments:
            if (
                instrument.code == InstrumentCode.USD_M_FUTURE
                and instrument.is_active
                and not instrument.is_expired
            ):
                instrument.start_futures_processes()

        self.t = Thread(target=self._update_ticker, args=(), daemon=True)
        self.t.start()

    def _get_ticker_data(self, instr_idx):
        instrument = self.instruments[instr_idx]
        mark_price = instrument.orderbook.get_mark_price()

        data = {
            "base_currency": instrument.base_currency.symbol,
            "best_ask_amount": instrument.orderbook.get_best_ask_size(),
            "best_ask_price": instrument.orderbook.get_best_ask_price(),
            "best_bid_amount": instrument.orderbook.get_best_bid_size(),
            "best_bid_price": instrument.orderbook.get_best_bid_price(),
            "code": instrument.code,
            "contract_size": instrument.contract_size,
            "estimated_delivery_price": 0,
            "index_price": instrument.index.get_index_price(),
            "instrument": instrument.name,
            "instrument_name": instrument.name,
            "interest_value": 0,
            "last_price": instrument.orderbook.get_last_price(),
            "mark_price": mark_price,
            "open_interest": instrument.orderbook.get_open_interest(),
            "quote_currency": instrument.quote_currency.symbol,
            "settlement_price": "NaN",
            "state": instrument.orderbook.state,
            "timestamp": time.time(),
            "asks": list(
                map(
                    lambda order: [order.price, order.remainingToFill],
                    instrument.orderbook.asks,
                )
            ),
            "bids": list(
                map(
                    lambda order: [order.price, order.remainingToFill],
                    instrument.orderbook.bids,
                )
            ),
            "stats": {
                "volume_usd": instrument.orderbook.stats["volume_usd"],
                "volume": instrument.orderbook.stats["volume"],
                "price_change": instrument.orderbook.stats["price_change"],
                "low": instrument.orderbook.stats["low"],
                "high": instrument.orderbook.stats["high"],
            },
        }
        return data

    def _update_ticker(self):
        while True:
            events = []

            for instr in self.instruments:
                instr_idx = self._instrument_idxs[instr.name]
                instrument = self.instruments[instr_idx]
                index_price = instrument.get_index_price()
                # logger.info(f"$$$$$$$$$$$$$ last traded price {instrument.orderbook.get_last_price()}")

                #  do not update the ticker if price has not arrived yet
                if index_price == 0:
                    continue
                ticker_data = self._get_ticker_data(instr_idx)
                # update tickers iglobally
                self.tickers[instr.name] = ticker_data

                # publish ticker updates to users after removing instrument code
                del ticker_data["code"]
                events.append(
                    {
                        "channel": "ticker." + instr.name,
                        "data": ticker_data,
                    }
                )

            for index in self.indices:
                price = index.get_index_price()
                if price > 0:
                    events.append(
                        {
                            "channel": "price_index." + index.name,
                            "data": {
                                "price": price,
                                "index_name": index.name,
                                "timestamp": time.time(),
                            },
                        }
                    )
            if len(events) > 0:
                self.producer.produce_multiple(
                    events,
                    "public_subs",
                )
            time.sleep(2)


    def set_price_feed(self, index_name, price, confidence_interval=None):
        self.price_feed[index_name] = price

    
    def handle_msg(self, msg_dict):
        self.msgs.append(msg_dict)
        method = msg_dict["method"]

        # params -> instrument_name
        if(method == "public/get_trades_by_instrument"):
            try:
                return {
                    "status": "success",
                    "response": [
                        x.getObj()
                        for x in self.trades[msg_dict["params"]["instrument_name"]][
                            -1:-21:-1
                        ]
                    ],
                }
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
            
        # params -> none
        elif method == "public/get_index_price_names":
            try:
                return {
                    "status": "success",
                    "response": self.supported_indices,
                }
            except:
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }

        # params -> none
        elif method == "public/get_currencies":
            try:
                return {
                    "status": "success",
                    "response": self.tradable_asset_symbols,
                } 
            except:
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
            
        # params -> instrument_name
        elif method == "public/ticker":
            try:
                instrument_name = msg_dict["params"]["instrument_name"]
                instr_idx = self._instrument_idxs[instrument_name]
                return {
                    "status": "success",
                    "response": self._get_ticker_data(instr_idx),
                }
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
            
        # params -> index_name
        elif method == "public/get_index_price":
            try:
                index_name = msg_dict["params"]["index_name"]
                index_idx = self._index_idxs[index_name]

                return {
                    "status": "success",
                    "response": {
                        "price": self.indices[index_idx].get_index_price(),
                        "index_name": index_name,
                        "timestamp": time.time(),
                    },
                }
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }

        # params ->  none
        elif method == "public/get_all_instrument_names":
            try:
                return {
                    "status": "success",
                    "response": self.supported_instrument_names,
                }
            except:
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }

        # params ->  none
        elif method == "public/get_instruments":
            try:
                return {
                    "status": "success",
                    "response": self.instruments,
                }
            except:
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
            
        # params -> instrument_name, depth
        elif method == "public/get_order_book":
            try:
                instrument_name = msg_dict["params"]["instrument_name"]
                depth = msg_dict["params"]["depth"]
                instr_idx = self._instrument_idxs[instrument_name]
                orderbook_data = self._get_orderbook_data(instr_idx, depth)
                return {
                    "status": "success",
                    "response": orderbook_data,
                }
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
            
        elif method == "health_check":
            try:
                return {
                    "status": "success",
                    "response": "health good",
                }
            except:
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
                    
            
        # params -> {
        #   "BTC/USDC":20000,
        #   "ETH/USDC":2000
        # }
        elif method == "private/handle_pricefeed_updates":
            try:
                index_name = msg_dict["params"]["index_name"]
                price = msg_dict["params"]["price"]
                self.set_price_feed(index_name=index_name, price=price)

                return {
                    "status": "success",
                    "response": msg_dict["params"]
                }
            except:
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }   

        #params
        # from
        elif method == "private/get_deposits":
            try:
                is_account_available = "from" in msg_dict["params"]
                if is_account_available and msg_dict["params"]["from"] not in self.accounts:
                    self._generateAccount(from_addr=msg_dict["params"]["from"])

                return self.accounts[msg_dict["params"]["from"]]["deposits"]  
            except:    
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }   
            

        #params
        # from
        elif method == "private/get_withdrawals":
            try:
                is_account_available = "from" in msg_dict["params"]
                if is_account_available and msg_dict["params"]["from"] not in self.accounts:
                    self._generateAccount(from_addr=msg_dict["params"]["from"])

            # TODO: Transfer amount from on chain

                return self.accounts[msg_dict["params"]["from"]]["withdrawals"]  
            except:    
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }   



        # params
        # from
        # currency
        # amount
        elif method == "private/deposit":
            print(msg_dict)
            try:
                is_account_available = "from" in msg_dict["params"]
                if is_account_available and msg_dict["params"]["from"] not in self.accounts:
                    self._generateAccount(from_addr=msg_dict["params"]["from"])
                res = self._add_coll(msg_dict)
                return res
            
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }  
            

        # params
        # from
        # currency
        # amount
        elif method == "private/withdraw":
            try:
                is_account_available = "from" in msg_dict["params"]
                if is_account_available and msg_dict["params"]["from"] not in self.accounts:
                    self._generateAccount(from_addr=msg_dict["params"]["from"])

                res = self._withdraw_coll(msg_dict)
                return res
            
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }  
    
        # params
        # from
        elif method == "private/get_collateral":
            try:
                return {'USDC': self.accounts[msg_dict["params"]["from"]]["collateral"][self.supported_colls[0]]}
            
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }  
            
        # params
        # from
        elif method == "private/get_all_trades":
            try:
                return self.accounts[msg_dict["params"]["from"]]["trades"]
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
            
        # params
        # from  
        elif method == "private/get_positions":
            try:
                is_account_available = "from" in msg_dict["params"]
                if is_account_available and msg_dict["params"]["from"] not in self.accounts:
                    self._generateAccount(from_addr=msg_dict["params"]["from"])
                return {
                    "status": "success",
                    "response": self._refresh_account_positions(msg_dict["params"]["from"]),
                }
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
            
        # params
        # from  
        elif method == "private/get_account_summary":
            try:
                account_addr = msg_dict["params"]["from"]
                self._refresh_account_positions(account_addr)
                pnl = 0
                for instrument_name in self.accounts[account_addr]["positions"]:
                    position = self.accounts[account_addr]["positions"][instrument_name]
                    if position:
                        pnl += position["unrealized_pnl"]
                all_positions = self.accounts[account_addr]["positions"]
                all_open_orders = self.accounts[account_addr]["open_orders"]
                all_instruments_data = self.tickers


                margin = calculate_total_margin_required(self.accounts[account_addr]["positions"], self.accounts[account_addr]["open_orders"])
                equity = self.accounts[account_addr]["collateral"][self.supported_colls[0]]

                available_margin = equity - margin

                return {
                    "status": "success",
                    "response": {
                        "total_pl": float(pnl),                   
                        "margin": float(available_margin),
                        "equity": float(
                            self.accounts[account_addr]["collateral"][self.supported_colls[0]]
                        ),
                        "currency": 'USDC',
                        "balance": float(
                            self.accounts[account_addr]["collateral"][self.supported_colls[0]] - margin
                        ),
                        "available_withdrawal_funds": float(
                            (self.accounts[account_addr]["collateral"][self.supported_colls[0]]) - margin
                        ),
                    },
                }
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
        
        # params
        # from
        elif method == "private/get_open_orders":
            try:
                account_addr = msg_dict["params"]["from"]
                is_account_available = "from" in msg_dict["params"]
                if is_account_available and msg_dict["params"]["from"] not in self.accounts:
                    self._generateAccount(from_addr=msg_dict["params"]["from"])

                return {
                    "status": "success",
                    "response": self.accounts[account_addr]["open_orders"],
                }
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
            
        #params
        # type -> limit/market
        # instrument_name
        # from
        # amount (number of contracts)
        # leverage
        # price

        elif method == "private/buy":
            try:
                print(msg_dict)
                msg_dict["params"]["amount"] = float(msg_dict["params"]["amount"])
                msg_dict["params"]["leverage"] = int(msg_dict["params"]["leverage"])
                print(msg_dict)
                account_addr = msg_dict["params"]["from"]
                is_account_available = "from" in msg_dict["params"]
                if is_account_available and msg_dict["params"]["from"] not in self.accounts:
                    self._generateAccount(from_addr=msg_dict["params"]["from"])

                if msg_dict["params"]["type"] == "limit":
                    msg_dict["params"]["price"] = float(msg_dict["params"]["price"])
                    res = self._handle_lmt_order(msg_dict)
                    return res
                elif msg_dict["params"]["type"] == "market":
                    res = self._handle_mkt_order(msg_dict)
                    return res
                else:
                    return {
                        "status": "error",
                        "response": "unsupported buy order type",
                    }
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }
            
        elif method == "private/sell":
            msg_dict["params"]["amount"] = float(msg_dict["params"]["amount"])
            msg_dict["params"]["leverage"] = int(msg_dict["params"]["leverage"])
            try:
                account_addr = msg_dict["params"]["from"]
                is_account_available = "from" in msg_dict["params"]
                if is_account_available and msg_dict["params"]["from"] not in self.accounts:
                    self._generateAccount(from_addr=msg_dict["params"]["from"])

                if msg_dict["params"]["type"] == "limit":
                    msg_dict["params"]["price"] = float(msg_dict["params"]["price"])
                    res = self._handle_lmt_order(msg_dict)
                    return res
                elif msg_dict["params"]["type"] == "market":
                    res = self._handle_mkt_order(msg_dict)
                    return res
                else:
                    return {
                        "status": "error",
                        "response": "unsupported sell order type",
                    }
            except Exception as e:
                logger.error(e)
                return {
                    "status": "failed",
                    "respomse": "Some error occured"
                }

        #params
        # from
        elif method == "private/get_account_details":
            try:
                from_addr = msg_dict["params"]["from"]
                if from_addr not in self.accounts:
                    self._generateAccount(from_addr)

                self._refresh_account_positions(from_addr)

                acc = self.accounts[from_addr]
                positions = acc["positions"]
                open_orders = acc["open_orders"]
                collateral = acc["collateral"][self.supported_colls[0]]
                available_margin = acc["available_margin"][self.supported_colls[0]]
                trades = acc["trades"]
                deposits = acc["deposits"]
                withdrawals = acc["withdrawals"]

                
                return {"status": "success", "response": {"positions": positions, "open_orders": open_orders, "collateral": collateral, "trades": trades, "deposits": deposits, "withdrawals": withdrawals, "available_margin": available_margin}}
            except:
                return {"status": "failed", "response": "some error occured"}

        # TODO: Methods to add ->  cancel, cancel_all


    def _handle_mkt_order(self, order_dict: dict):
        instrument_name = order_dict["params"]["instrument_name"]
        instrument = self._get_instrument_from_name(instrument_name)
        self._refresh_account_positions(order_dict["params"]["from"])

        account_addr = order_dict["params"]["from"]
        account = self.accounts[account_addr]
        account_collateral = account["collateral"]

        order_contracts_size = float(
            order_dict["params"]["amount"]
        )
        leverage = order_dict["params"]["leverage"]

        order = MarketOrder(
            fromaddr=account_addr,
            order_id=str(uuid1()),
            side=Side.BUY if order_dict["method"] == "private/buy" else Side.SELL,
            size=order_contracts_size,
            leverage=leverage,
            time_in_force="GTC"
        )

        margin = (order_contracts_size * instrument.index.get_index_price())/leverage
        print("Check nargin for new position")
        print(margin)

        # Margin checks for market order
        ### Check the net margin of the position after market order

        print("Final position is")
        final_margin = self.change_in_final_future_margin(instrument, account_addr, "buy" if order_dict["method"] == "private/buy" else "sell", order_contracts_size,margin, leverage, instrument.index.get_index_price())
        print(final_margin)
        print(account["collateral"][self.supported_colls[0]])

        if(final_margin > account["collateral"][self.supported_colls[0]]):
            return {
                "status": "failure",
                "response": {
                    "Not enough margin"
                },
            }
        


        if True:
            (
                executed_trades_while_at_process,
                updated_orders,
                filled_orders,
                cancelled_orders,
                involved_accounts,
            ) = instrument.orderbook.process_order(order)

            print("printing esxecuting trades ")
            print(executed_trades_while_at_process)

            self.trades[instrument_name] += executed_trades_while_at_process

            self._update_account_positions(
                executed_trades_while_at_process,
                leverage,
                instrument,
            )

            self._update_account_orders(
                updated_orders,
                filled_orders,
                cancelled_orders,
                instrument,
            )
            all_user_trades = []

            for trade in executed_trades_while_at_process:
                trade = trade.getObj()
                all_user_trades.append(
                    {
                        "data": {
                            "price": trade["price"],
                            "side": "sell" if trade["side"] == "buy" else "buy",
                            "size": trade["size"],
                            "leverage": leverage,
                            "liquidity": "maker",
                            "timestamp": trade["timestamp"],
                            "instrument_name": order_dict["params"]["instrument_name"],
                            "order_type": "limit",
                        },
                        "account": trade["maker"],
                    }
                )
                all_user_trades.append(
                    {
                        "data": {
                            "price": trade["price"],
                            "side": trade["side"],
                            "size": trade["size"],
                            "leverage": leverage,
                            "liquidity": "maker",
                            "timestamp": trade["timestamp"],
                            "instrument_name": order_dict["params"]["instrument_name"],
                            "order_type": "limit",
                        },
                        "account": trade["taker"],
                    }
                )
            return {
                "status": "success",
                "response": {
                    "order": order_dict["params"],
                    "trades": [x.toJSON() for x in executed_trades_while_at_process],
                },
            }




    def _handle_lmt_order(self, order_dict: dict):

        instrument_name = order_dict["params"]["instrument_name"]
        instrument = self._get_instrument_from_name(instrument_name)
        self._refresh_account_positions(order_dict["params"]["from"])

        account_addr = order_dict["params"]["from"]
        account = self.accounts[account_addr]
        account_collateral = account["collateral"]


        order_contracts_size = float(
            order_dict["params"]["amount"]
        )
        leverage = order_dict["params"]["leverage"]

        # check margin
        margin = (order_contracts_size * float(order_dict["params"]["price"]))/leverage
        print("Check nargin for new position")
        print(margin)

        # Margin checks for market order
        ### Check the net margin of the position after market order

        print("Final position is")
        final_margin = self.change_in_final_future_margin(instrument, account_addr, "buy" if order_dict["method"] == "private/buy" else "sell", order_contracts_size,margin, leverage, float(order_dict["params"]["price"]))
        print(final_margin)
        print(account["collateral"][self.supported_colls[0]])

        if(final_margin > account["collateral"][self.supported_colls[0]]):
            return {
                "status": "failure",
                "response": {
                    "Not enough margin"
                },
            }

        order = LimitOrder(
            fromaddr=account_addr,
            order_id=str(uuid1()),
            side=Side.BUY if order_dict["method"] == "private/buy" else Side.SELL,
            size=order_contracts_size,
            leverage=int(leverage),
            price=float(order_dict["params"]["price"]),
            time_in_force="GTC"
        )



        (
                executed_trades_while_at_process,
                updated_orders,
                filled_orders,
                cancelled_orders,
                involved_accounts,
            ) = instrument.orderbook.process_order(order)
        self.trades[instrument_name] += executed_trades_while_at_process
        self._update_account_positions(
                executed_trades_while_at_process,
                leverage,
                instrument,
            )
        print(2)
        self._update_account_orders(
                updated_orders,
                filled_orders,
                cancelled_orders,
                instrument,
            )
        all_user_trades = []
        print(3)

        for trade in executed_trades_while_at_process:
                trade = trade.getObj()
                all_user_trades.append(
                    {
                        "data": {
                            "price": trade["price"],
                            "side": "sell" if trade["side"] == "buy" else "buy",
                            "size": trade["size"],
                            "leverage": leverage,
                            "liquidity": "maker",
                            "timestamp": trade["timestamp"],
                            "instrument_name": order_dict["params"]["instrument_name"],
                            "order_type": "limit",
                        },
                        "account": trade["maker"],
                    }
                )
                all_user_trades.append(
                    {
                        "data": {
                            "price": trade["price"],
                            "side": trade["side"],
                            "size": trade["size"],
                            "leverage": leverage,
                            "liquidity": "maker",
                            "timestamp": trade["timestamp"],
                            "instrument_name": order_dict["params"]["instrument_name"],
                            "order_type": "limit",
                        },
                        "account": trade["taker"],
                    }
                )
                print(4)
        return {
            "status": "success",
            "response": {
            "order": order_dict["params"],
                "trades": [x.toJSON() for x in executed_trades_while_at_process],
            },
        }
    
    def _update_account_orders(
        self, updated_orders, filled_orders, cancelled_orders, instrument
    ):
        for order_id in updated_orders:
            order = updated_orders[order_id]
            if updated_orders[order_id]["class"] == "LimitOrder":
                account_addr = updated_orders[order_id]["fromaddr"]
                self.accounts[account_addr]["open_orders"][instrument.name][order_id] = order

        for order_id in filled_orders:
            account_addr = filled_orders[order_id]["fromaddr"]
            if (
                order_id
                in self.accounts[account_addr]["open_orders"][instrument.name]
            ):
                del self.accounts[account_addr]["open_orders"][instrument.name][order_id]
        for order_id in cancelled_orders:
            account_addr = cancelled_orders[order_id]["fromaddr"]
            del self.accounts[account_addr]["open_orders"][instrument.name][order_id]


    def _update_account_positions(self, trades, leverage , instrument):
        for trade in trades:
            if trade.side == Side.BUY:
                # taker is buyer
                self._update_futures_position(
                    trade.taker, trade, Side.BUY, instrument, leverage
                )
                # maker is seller
                self._update_futures_position(
                    trade.maker, trade, Side.SELL, instrument, leverage
                )
            else:
                # taker is seller
                self._update_futures_position(
                    trade.taker, trade, Side.SELL, instrument, leverage
                )
                # maker is buyer
                self._update_futures_position(
                    trade.maker, trade, Side.BUY, instrument, leverage
                )

    def change_in_final_future_margin(self, instrument, from_add, side, size, margin , leverage, price):
        instrument_name = instrument.name
        instrument_base_currency = instrument.base_currency.symbol
        instrument_mark_price = instrument.get_mark_price()
        instrument_index_price = instrument.get_index_price()
        account_positions = self.accounts[from_add]["positions"]

        if not account_positions[instrument_name]:
            return margin
        
        else:
            instrument_position = account_positions[instrument_name]
            old_avg_price = instrument_position["average_price"]
            old_pos_size = instrument_position["size"]
            old_leverage = instrument_position["leverage"]
            old_margin = instrument_position["margin"]

            new_avg_price = price
            new_size = size if side=="buy" else -size
            new_leverge = leverage


            # case 1 -> increase position size
            if((old_pos_size > 0 and new_size>0) or (old_pos_size < 0 and new_size<0)):
                ## just add the positions sizes
                return margin
            
            # case2 -> decrease position size
            elif((old_pos_size>0 and new_size > 0 and old_pos_size>new_size) or (old_pos_size < 0 and new_size<0 and abs(old_pos_size)>abs(new_size))):
                # no new margin required
                return 0
            
            elif(((old_pos_size>0 and new_size < 0 ) or (old_pos_size < 0 and new_size>0 ))):
                margin_to_be_free = old_margin
                new_position_size = abs(old_pos_size - new_size)
                new_leverge = leverage
                new_margin_required = (new_position_size*price)/leverage
                if(margin_to_be_free > new_margin_required):
                    return 0
                else:
                    return (new_margin_required - margin_to_be_free)
                
            elif((old_pos_size > 0 and new_size <  0 and (abs(new_size) == abs(old_pos_size))) or  (old_pos_size < 0 and new_size > 0 and (abs(new_size) == abs(old_pos_size))) ):
                return 0


    def _update_futures_position(self, account, trade, trade_side, instrument, leverage):
        instrument_name = instrument.name
        instrument_base_currency = instrument.base_currency.symbol
        instrument_mark_price = instrument.get_mark_price()
        instrument_index_price = instrument.get_index_price()
        account_positions = self.accounts[account]["positions"]
        direction = "buy" if trade_side == Side.BUY else "sell"

        # In number of contracts--> ETH, BTC
        trade_size = trade.size if trade_side == Side.BUY else -trade.size

        #  In USD
        trade_price = trade.price
        print("Printitng trade info")
        print(trade)
        if not account_positions[instrument_name]:

            unrealized_pnl = (
                (instrument_mark_price - trade_price)
                * trade_size
                * instrument.contract_size
            )
            margin = (trade_price* abs(trade_size))/leverage
            # reduce margin from account
            # account["collateral"][self.supported_colls[0]] -= margin

            liquidation_price = trade_price - (margin/trade_size)
            account_positions[instrument_name] = {
                "average_price": trade_price,
                "contract_size": instrument.contract_size,
                "direction": direction,
                "estimated_liquidation_price": liquidation_price,
                "floating_profit_loss": "NA",
                "index_price": instrument_index_price,
                "instrument_name": instrument.name,
                "interest_value": "NA",
                "margin": margin,
                "leverage": leverage,
                "mark_price": instrument_mark_price,
                "realized_funding": 0,
                "settlement_price": 0,
                "size": trade_size,
                "unrealized_pnl": unrealized_pnl,
            }
            print("printing new position")
            print(account_positions[instrument_name])

        else:
            # if the account has an existing position
            instrument_position = account_positions[instrument_name]

            old_avg_price = instrument_position["average_price"]
            old_pos_size = instrument_position["size"]
            old_leverage = instrument_position["leverage"]
            old_margin = instrument_position["margin"]

            new_size = trade_size = trade.size if trade_side == Side.BUY else -trade.size
            margin = (trade_price* abs(trade_size))/leverage

            # updating average price
            if (old_pos_size > 0 and new_size > 0) or (
                old_pos_size < 0 and new_size < 0
            ):
                
                new_avg_price = ((old_avg_price * old_pos_size) + (new_size * trade_price))/(old_pos_size + new_size)
                new_margin = old_margin + margin
                new_leverage = ((old_pos_size + new_size)*new_avg_price)/new_margin
                new_pos_size = (old_pos_size + new_size)
                new_liquidation_price = new_avg_price - (new_margin/new_pos_size)

                instrument_position["average_price"] = new_avg_price
                instrument_position["margin"] = new_margin
                instrument_position["leverage"] = leverage
                instrument_position["size"] = new_pos_size
                instrument_position["estimated_liquidation_price"] = new_liquidation_price
                print("Updated instrument position is ")
                print(instrument_position)


            elif((old_pos_size > 0 and new_size < 0 and (abs(old_pos_size) > abs(new_size))) or (old_pos_size < 0 and new_size > 0 and (abs(old_pos_size) > abs(new_size) ))):
                
                new_pos_size = old_pos_size + new_size
                new_leverage = old_leverage
                new_avg_price = instrument_position["average_price"]
                new_margin = abs(new_pos_size * trade_price /new_leverage)
                new_liquidation_price = new_avg_price - (new_margin/new_pos_size)


                instrument_position["average_price"] = new_avg_price
                instrument_position["margin"] = new_margin
                instrument_position["leverage"] = new_leverage
                instrument_position["size"] = new_pos_size
                instrument_position["estimated_liquidation_price"] = new_liquidation_price

                print("Updated instrument position is ")
                print(instrument_position)

            elif((old_pos_size > 0 and new_size < 0 and (abs(old_pos_size) < abs(new_size))) or (old_pos_size < 0 and new_size > 0 and (abs(old_pos_size) < abs(new_size) ))):

                new_pos_size = old_pos_size + new_size
                new_leverage = leverage
                new_avg_price = trade_price
                new_margin = abs(new_pos_size*trade_price/new_leverage)
                new_liquidation_price = new_avg_price - (new_margin/new_pos_size)

                instrument_position["average_price"] = new_avg_price
                instrument_position["margin"] = new_margin
                instrument_position["leverage"] = new_leverage
                instrument_position["size"] = new_pos_size
                instrument_position["estimated_liquidation_price"] = new_liquidation_price
                print("Updated instrument position is ")
                print(instrument_position)

            elif((old_pos_size > 0 and new_size <  0 and (abs(new_size) == abs(old_pos_size))) or  (old_pos_size < 0 and new_size > 0 and (abs(new_size) == abs(old_pos_size))) ):
                print("removing position")
                del account_positions[instrument_name]
                account_positions[instrument_name] = {}
                return

            unrealized_pnl = (
                (instrument_mark_price - instrument_position["average_price"])
                * new_pos_size
            )
            instrument_position["unrealized_pnl"] = unrealized_pnl
            # updating position direction
            if instrument_position["size"] > 0:
                instrument_position["direction"] = "buy"
            elif instrument_position["size"] < 0:
                instrument_position["direction"] = "sell"
            else:
                instrument_position["direction"] = "zero"


    def _refresh_account_positions(self, account_addr):
        all_open_orders = self.accounts[account_addr]["open_orders"]
        all_positions = self.accounts[account_addr]["positions"]
        all_instruments_data = self.tickers

        try:
            margin = calculate_total_margin_required(self.accounts[account_addr]["positions"], self.accounts[account_addr]["open_orders"])
            equity = self.accounts[account_addr]["collateral"][self.supported_colls[0]]
            print("MArgin and equity")

            self.accounts[account_addr]["available_margin"][self.supported_colls[0]] = equity - margin

        except Exception as e:
            print(e)
            pass


        for instrument_name in self.accounts[account_addr]["positions"]:
            position = all_positions[instrument_name]
            instrument = self._get_instrument_from_name(instrument_name)
            if(position):
                mark_price = instrument.orderbook.get_mark_price()
                index_price = instrument.orderbook.get_mark_price()
                average_price = position["average_price"]
                position_size = position["size"]
                direction = position["direction"]

                
                unrealized_pnl = self._calculate_unrealized_pnl(
                    mark_price,
                    average_price,
                    position_size,
                    direction
                )

                position["index_price"] = index_price
                position["mark_price"] = mark_price
                position["unrealized_pnl"] = unrealized_pnl
                position["size_usd"] = average_price*position_size
                
        return self.accounts[account_addr]["positions"]



    def _calculate_unrealized_pnl(self,mark_price, average_price, position_size,  direction):
        if(direction == 'buy'):
            return (mark_price - average_price)*abs(position_size)
        else:
            return (average_price - mark_price)*abs(position_size)


    def _get_instrument_from_name(self, instrument_name):
        instr_idx = self._instrument_idxs[instrument_name]
        instrument = self.instruments[instr_idx]
        return instrument


    def _withdraw_coll(self, msg_dict):
            account_addr = msg_dict["params"]["from"]
            withdraw_currency = msg_dict["params"]["currency"]
            collateral_to_withdraw = msg_dict["params"]["amount"]
            
            self._refresh_account_positions(msg_dict["params"]["from"])

            account_addr = msg_dict["params"]["from"]
            account_withdrawals = self.accounts[account_addr]["withdrawals"]
            account_collateral = self.accounts[account_addr]["collateral"]
            if(self.accounts[account_addr]["available_margin"][self.supported_colls[0]] > collateral_to_withdraw):
                account_collateral[self.supported_colls[0]]  -= collateral_to_withdraw         
            else:
                return {
                            "status": "error",
                            "response": "Not enough balance to withdraw",
                        }
            new_withdrawal = {
                    "amount": collateral_to_withdraw,
                    "balance": account_collateral[self.supported_colls[0]],
                    "currency": withdraw_currency,
                    # "timestamp": int(1e6 * time()),
                    "status": "confirmed",
                }
            account_withdrawals["USDC"] = [new_withdrawal]
            return {
                    "status": "success",
                    "response": {
                        "amount": collateral_to_withdraw,
                        "balance": account_collateral[self.supported_colls[0]],
                        "currency": withdraw_currency,
                        # "timestamp": int(1e6 * time()),
                        "status": "confirmed",
                    },
                }



    def _add_coll(self, msg_dict):
        deposit_currency = msg_dict["params"]["currency"]
        collateral_to_add = msg_dict["params"]["amount"]

        if deposit_currency in self.supported_coll_symbols:

                account_addr = msg_dict["params"]["from"]
                account_deposits = self.accounts[account_addr]["deposits"]
                account_collateral = self.accounts[account_addr]["collateral"]
                

                if account_collateral[self.supported_colls[0]] is not None:
                #     # repeat deposit
                    account_collateral[self.supported_colls[0]] += collateral_to_add
                else:
                #     # first deposit
                    account_collateral[self.supported_colls[0]] = collateral_to_add

                new_deposit = {
                    "amount": collateral_to_add,
                    "balance": account_collateral[self.supported_colls[0]],
                    "currency": deposit_currency,
                    # "timestamp": int(1`e6 * time()),
                    "status": "confirmed",
                }
                account_deposits["USDC"] = [new_deposit]

                return {
                    "status": "success",
                    "response": {
                        "amount": collateral_to_add,
                        "balance": account_collateral[self.supported_colls[0]],
                        "currency": deposit_currency,
                        # "timestamp": int(1e6 * time()),
                        "status": "confirmed",
                    },
                }
        else:
            # unsupported deposit currency
            return {
                "status": "error",
                "response": "unsupported collateral",
            }


    def _generateAccount(self, from_addr ):
            self.users.append(from_addr)
            self.accounts[from_addr] = {
                "is_at_risk": False,
                # tradable_asset (ETH, BTC) ---> instrument_name ---> order_id ---> order
                "open_orders": {k: {} for k in self.supported_instrument_names},
                # tradable_asset (ETH, BTC ) ---> kind ---> instrument_name
                "positions": {k : {} for k in self.supported_instrument_names},
                # coll_asset (USDT, USDC, DAI) ---> 10_000( in dev env )
                "collateral": {
                    k: 0 for k in self.supported_colls
                },
                "available_margin": {
                    k: 0 for k in self.supported_colls
                },
                "trades": {},
                "deposits": {"USDC": []},
                "withdrawals": {"USDC": []},
                "settlements": {},
                "portfolio_margins": {k: {} for k in self.tradable_asset_symbols},
                "is_portfolio_margined": True,
                "max_open_orders": 10_000,
            }

    def _marketMakerLimitOrder(self,from_addr, instrument_name, buy:bool, contracts_size, price):
        if from_addr not in self.accounts:
            self._generateAccount(from_addr)

        id=str(uuid1())
        order = LimitOrder(
            fromaddr=from_addr,
            order_id=id,
            side=Side.BUY if buy else Side.SELL,
            size=contracts_size,
            leverage=10,
            price=price,
            time_in_force="GTC",
        )
        instr_idx = self._instrument_idxs[instrument_name]
        instrument = self.instruments[instr_idx]
        instrument.orderbook.process_order(order)
        return id
    
    def _marketTakerMarketOrder(self,from_addr,instrument_name, buy:bool, contracts_size):
        if from_addr not in self.accounts:
            self._generateAccount(from_addr)
        id=str(uuid1())
        order = MarketOrder(
            fromaddr=from_addr,
            order_id=id,
            side=Side.BUY if buy else Side.SELL,
            size=contracts_size,
            leverage=10,
            time_in_force="GTC"
        )
        instr_idx = self._instrument_idxs[instrument_name]
        instrument = self.instruments[instr_idx]
        instrument.orderbook.process_order(order)
        return id
    def _cancelOrder(self, from_addr, order_id, instrument_name):

        order = CancelOrder(
            fromaddr=from_addr,
            order_id=order_id,
        )
        instr_idx = self._instrument_idxs[instrument_name]
        instrument = self.instruments[instr_idx]
        instrument.orderbook.process_order(order)
        

    def _get_orderbook_data(self, instr_idx, depth):
            instrument = self.instruments[instr_idx]
            logger.info(instrument.name)
            asks = instrument.orderbook.bids
            bids = instrument.orderbook.asks
            if len(bids) == 0:
                required_bids = []
            elif (len(bids) < depth):
                required_bids = bids
            else:
                required_bids = bids[:depth]

            if len(asks) == 0:
                required_asks = []
            elif (len(asks) < depth):
                required_asks = asks
            else:
                required_asks = asks[:depth]
            return {"bids": required_bids, "asks": required_asks}

       