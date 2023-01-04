import os
import datetime as dt
import pandas as pd

import processing


def main(charts_path: str):
    for dirname, _, filenames in os.walk(charts_path):
        for filename in filenames:
            country_code = dirname.replace('\\', '/').split('/')[-1]
            date_str = filename.split("--")[0]
            date_dt = dt.datetime.strptime(date_str, "%Y-%m-%d")
            chart_info = pd.Series({
                'country_code': country_code,
                'date': date_dt
            })
            chart = pd.read_csv(f"{dirname}/{filename}", sep=';')
            processing.create_chart(chart_info, chart)


if __name__ == "__main__":
    charts_path = os.path.join(os.environ['DATA_PATH'], "charts")
    main(charts_path)
