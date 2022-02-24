import csv, json

def main():
    with open("timeline.csv", "r") as f:
        csv_reader = csv.reader(f, delimiter=',')
        rows = [row for row in csv_reader]
    data = {}
    for row in rows:
        id, group, section, date, title, name, speech = row
        if group not in data:
            data[group] = {
                "id": group[:-5],
                "date": date,
                "title": title,
                "speeches": [
                    {
                        "name": name,
                        "speech": speech
                    }
                ]
            }
        else:
            data[group]["speeches"].append({
                "name": name,
                "speech": speech
            })
    with open("events.js", "w") as js:
        js.write("const events = [\n")
        for k, v in data.items():
            id = v["id"]
            date = v["date"]
            title = v["title"]
            speeches = v["speeches"]
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