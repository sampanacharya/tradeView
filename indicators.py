def GANN_range(high_val, low_val):
    highValSqrt = high_val ** 0.5
    lowValSqrt = low_val ** 0.5

    g = highValSqrt * highValSqrt - lowValSqrt * lowValSqrt
    rangeGann = lowValSqrt

    res = []
    st = 0
    while(st != 1):
        res.append(rangeGann * rangeGann + st * g)
        st += 0.125
    
    return res

def RSI_rate_distance(df,instant_and_average_rate_distance = 90, instant_rate_period = 3, average_rate_period = 6, rsi_length = 30, rsi_value = 47):
    def derivative(src, period):
        return (src - src.shift(period)) / period

    src = df['Close']

    instant_and_average_rate_distance = instant_and_average_rate_distance
    instant_rate_period = instant_rate_period
    average_rate_period = average_rate_period

    rsi_length = rsi_length
    rsi_value = rsi_value

    d1 = derivative(src, instant_rate_period)
    d2 = derivative(src, average_rate_period)

    longCondition = d1 - d2 > instant_and_average_rate_distance and talib.RSI(src, rsi_length)[-1] > rsi_value

    plot_var = None
    if longCondition:
        plot_var = df['Close']
    else:
        plot_var = None
    print(plot_var)