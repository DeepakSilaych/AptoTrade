

def calculate_liquidation_price_of_position(position):
    avg_price = position["average_price"]
    leverage = position["leverage"]
    size = position["size"]

    margin = (size * avg_price)/leverage

    if(position["direction"] == "buy"):
        liquidation_price = avg_price - (margin / size)
    else:
        liquidation_price = avg_price + (margin / size)

    return liquidation_price
