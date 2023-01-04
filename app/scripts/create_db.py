import pandas as pd
import pycountry

import processing
from db import _conn, Base


def main():
    # Create all tables
    _conn.create_ddl(Base)
    # Create all countries
    countries = [(c.alpha_2.lower(), c.name) for c in pycountry.countries if c.alpha_2 != "gl"]
    countries.append(("gl", "global"))
    processing.create_countries(pd.DataFrame(countries, columns=['id', 'name']))


if __name__ == "__main__":
    main()
