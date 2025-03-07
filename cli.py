from datetime import datetime, timedelta

import pandas as pd

from icalendar import Calendar, Event
from minicli import cli, run
from slugify import slugify

DATE_FMT = "%m/%d/%Y"


@cli
def convert(*calendars, year="2025"):
    """
    Convert CSV source to ICS, filtering by calendar.

    :calendar: UCI calendar — defaults to World Tour for men (UWT) and women (MON)
    """
    if not calendars:
        calendars = ("UWT", "MON")

    df = pd.read_excel("data/UCICompetitions_ROA_2025.xls", skiprows=4)
    df = df[df.Calendar.isin(calendars)]
    df = df[df["Date From"].str.endswith(year)]

    if df.empty:
        print("No matching events found")
        return

    cal = Calendar()
    cal.add("prodid", f"-//UCI calendar({', '.join(calendars)})//france.sh//")
    cal.add("version", "2.0")
    cal.add("last-modified", datetime.now())

    for _, event in df.iterrows():
        cal_event = Event()
        slug = slugify(f"{event['Name']} - {event['Category']}")
        print(slug)
        cal_event.add("uid", f"{slug}@bulte.net")
        category = event["Category"] or "MW"
        cal_event.add("summary", f"{event['Name']} — {category} — {event['Country']}")
        start = datetime.strptime(event["Date From"], DATE_FMT).date()
        end = datetime.strptime(event["Date To"], DATE_FMT).date() + timedelta(days=1)
        cal_event.add("dtstart", start)
        cal_event.add("dtend", end)
        cal.add_component(cal_event)

    with open(f"data/uci-road-{'-'.join(calendars)}-{year}.ics", "wb") as ofile:
        ofile.write(cal.to_ical())

    df.to_csv(f"data/uci-road-{'-'.join(calendars)}-{year}.csv")


if __name__ == "__main__":
    run()
