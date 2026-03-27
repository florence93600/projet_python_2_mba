import time
import pandas as pd
from typing import Dict, Any, Optional

moment_depart = time.time()

def get_system_health(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:

    uptime_seconds = int(time.time() - moment_depart)
    hours, rem = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(rem, 60)


    is_ready = df is not None and isinstance(df, pd.DataFrame)


    return {
        "status": "healthy" if is_ready else "degraded",
        "uptime": f"{hours}h {minutes}m {seconds}s",
        "uptime_seconds": uptime_seconds,
        "dataset_ready": is_ready,
        "total_records": len(df) if is_ready else 0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "service": "Transaction API System Service"
    }
