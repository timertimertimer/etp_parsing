from .libraries import *


class OfferParse:
    def __init__(self, response_):
        self.response = response_
        self.soup = soup(self.response)

    def get_period_table(self):
        table = self.soup.find("table", class_="trades_table")
        if table:
            df = pd.read_html(re.sub(r",", ".", str(table)))
            return df[0]
        return None

    @property
    def periods(self):
        check_value = int(10**20)
        periods = list()
        df = self.get_period_table()
        try:
            for t in range(len(df)):
                start_date_request = df.iloc[t][1]
                end_date_request = df.iloc[t][2]
                end_date_trading = df.iloc[t][2]
                current_price = df.iloc[t][-2]
                if not re.match(r"nan", str(current_price), re.IGNORECASE):
                    if isinstance(current_price, str):
                        current_price_ = make_float(current_price)
                    elif isinstance(current_price, float64):
                        current_price_ = round(float(current_price), 2)
                    elif isinstance(current_price, (int, integer)):
                        current_price_ = round(float(current_price), 2)
                    else:
                        logger.warning(
                            f"{self.response.url} | INVALID TYPE CURRENT PRICE"
                        )
                        current_price_ = None
                    period = {
                        "start_date_requests": DateTimeHelper.smart_parse(
                            re.sub(r"\s+", " ", start_date_request.replace("-", " "))
                        ).astimezone(DateTimeHelper.moscow_tz),
                        "end_date_requests": DateTimeHelper.smart_parse(
                            re.sub(r"\s+", " ", end_date_request.replace("-", " "))
                        ).astimezone(DateTimeHelper.moscow_tz),
                        "end_date_trading": DateTimeHelper.smart_parse(
                            re.sub(r"\s+", " ", end_date_trading.replace("-", " "))
                        ).astimezone(DateTimeHelper.moscow_tz),
                        "current_price": current_price_,
                    }
                    periods.append(period)
                    if check_value < current_price_:
                        logger.warning(
                            f"{self.response.url} | ERROR INVALID PRICE ON PERIOD - CURRENT PRICE HIGHER THAN PREVIUOS",
                            df,
                        )
                    check_value = current_price_
            return periods
        except Exception as e:
            logger.warning(f"{self.response.url} | ERROR PERIODS  {e}\n{df}")
            return None

    def get_start_date_request(self, lst_period: list):
        try:
            first_element: dict = lst_period[0]
            return first_element["start_date_requests"]
        except Exception as e:
            logger.warning(f"{self.response.url} | ERROR END DATE TRADING {e}")
        return None

    def get_end_date_request(self, lst_period: list):
        try:
            last_element: dict = lst_period[-1]
            return last_element["end_date_requests"]
        except Exception as e:
            logger.warning(f"{self.response.url} | ERROR END DATE TRADING {e}")
        return None

    def get_start_price(self, lst_periods):
        try:
            first_element: dict = lst_periods[0]
            return first_element["current_price"]
        except Exception as e:
            logger.warning(f"{self.response.url} | ERROR END DATE TRADING {e}")
        return None
