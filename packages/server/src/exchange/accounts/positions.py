class PositionHandler:
    def __init__(self, account_addr):
        self.instrument_name = account_addr
        self.all_positions = {}
        self.options_positions = {}
        self.inverse_perp_positions = {}
        self.linear_perp_positions = {}

    def get_position(self, instrument_name):
        return self.all_positions[instrument_name]

    def add_linear_perp_position(
        self, instrument_name, index_price, mark_price, order_size, order_side
    ):
        if instrument_name not in self.all_positions:
            linear_perp_position = LinearPerpPosition(
                index_price,
                mark_price,
                order_size,
                order_side,
            )
            self.linear_perp_positions[instrument_name] = linear_perp_position
            self.all_positions[instrument_name] = linear_perp_position
        else:
            pass

    def add_inverse_perp_position(
        self, instrument_name, index_price, mark_price, order_size, order_side
    ):
        if instrument_name not in self.all_positions:
            linear_perp_position = LinearPerpPosition(
                index_price,
                mark_price,
                order_size,
                order_side,
            )
            self.linear_perp_positions[instrument_name] = linear_perp_position
            self.all_positions[instrument_name] = linear_perp_position
        else:
            pass

    def add_option_position(
        self, instrument_name, index_price, mark_price, order_size, order_side
    ):
        if instrument_name not in self.all_positions:
            linear_perp_position = LinearPerpPosition(
                index_price,
                mark_price,
                order_size,
                order_side,
            )
            self.linear_perp_positions[instrument_name] = linear_perp_position
            self.all_positions[instrument_name] = linear_perp_position
        else:
            pass

    def refresh_linear_perp_position(self, instrument_name, index_price, mark_price):
        existing_position = self.all_positions[instrument_name]

    def refresh_inverse_perp_position(self, instrument_name, index_price, mark_price):
        existing_position = self.all_positions[instrument_name]

    def refresh_option_position(self, instrument_name, index_price, mark_price):
        existing_position = self.all_positions[instrument_name]


class OptionPosition:
    def __init__(
        self,
    ):
        pass


class LinearPerpPosition:
    def __init__(
        self,
        index_price,
        mark_price,
        order_size,
        order_side,
    ):
        pass


class InversePerpPosition:
    def __init__(
        self,
    ):
        pass
