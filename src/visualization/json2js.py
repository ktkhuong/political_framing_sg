import datetime, json, os

def load_report(fp):
    with open(f"events\\{fp}", "r") as f:
        report = json.load(f)
    return report

def format_date(date):
    day, month, year = date.split("-")
    return datetime.datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")

def main():    
    data = [load_report(fp) for fp in os.listdir("events") if fp.endswith(".json")]
    with open("events.js", "w") as js:
        js.write("const events = [\n")
        for item in data:
            id = item["id"]
            date = format_date(item["date"])
            title = item["title"]
            speeches = item["speeches"]
            item = {
                "unique_id": id,
                "start_date": {"year": date[:4], "month": date[5:7], "day": date[-2:]},
                "text": {"headline": title},
                "media": {
                    "url": "#",
                    "alt": "#",
                    "caption": "".join([f"<p><strong>{s['name']}</strong>: {s['speech']}</p>" for s in speeches])
                }
            }
            js.write(json.dumps(item))
            js.write(",\n")
        js.write("]")
        
if __name__ == "__main__":
    main()