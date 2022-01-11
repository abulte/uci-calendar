import csv

from datetime import datetime, timedelta

from icalendar import Calendar, Event
from minicli import cli, run
from slugify import slugify


@cli
def convert(*calendars):
    """
    Convert CSV source to ICS, filtering by calendar.

    :calendar: UCI calendar — defaults to World Tour for men (UWT) and women (MON)
    """
    if not calendars:
        calendars = ("UWT", "MON")

    with open("data/uci-road-2022.csv") as ifile:
        reader = csv.DictReader(ifile, delimiter=";")
        events = [x for x in reader if x["Calendar"] in calendars]

    if not events:
        print("No matching events found")
        return

    cal = Calendar()
    cal.add("prodid", f"-//UCI calendar({', '.join(calendars)})//bulte.net//")
    cal.add("version", "2.0")
    cal.add("last-modified", datetime.now())

    for event in events:
        cal_event = Event()
        slug = slugify(f"{event['Name']} - {event['Category']}")
        print(slug)
        cal_event.add("uid", f"{slug}@bulte.net")
        category = event["Category"][0] if event["Category"] else "MW"
        cal_event.add("summary", f"{event['Name']} — {category} — {event['Country']}")
        start = datetime.strptime(event["Date From"], "%d.%m.%Y").date()
        end = datetime.strptime(event["Date To"], "%d.%m.%Y").date() + timedelta(days=1)
        cal_event.add("dtstart", start)
        cal_event.add("dtend", end)
        cal.add_component(cal_event)

    with open(f"data/uci-road-{'-'.join(calendars)}.ics", "wb") as ofile:
        ofile.write(cal.to_ical())


if __name__ == "__main__":
    run()
