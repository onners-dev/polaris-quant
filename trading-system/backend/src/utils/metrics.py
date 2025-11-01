import numpy as np

def rmse(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

def sharpe_ratio(returns, risk_free_rate=0.0):
    arr = np.array(returns)
    excess = arr - risk_free_rate
    std = np.std(excess)
    if std < 1e-8:
        return 0.0
    return float(np.mean(excess) / std)

def max_drawdown(returns):
    wealth = (1 + np.array(returns)).cumprod()
    roll_max = np.maximum.accumulate(wealth)
    drawdown = (wealth - roll_max) / roll_max
    return float(np.min(drawdown))
