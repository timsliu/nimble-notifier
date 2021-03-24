# runner.py
#
# This program periodically runs all other programs and acts as the main loop

import util
import matcher
import fetch_data
import notifier

def run_all():
    gmail_service = gmail_utils.GetService()

    vaccine_spotter = fetch_data.fetch_vaccine_spotter()
    vaccine_spotter.fetch()
    match_list = matcher.match_all()

    notifier.send_all(match_list, gmail_service)


if __name__ == "__main__":
    run_all()
