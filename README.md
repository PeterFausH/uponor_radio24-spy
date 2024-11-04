## Name
Uponor_Radio24-spy

## Description
even uponor radio24_at_home from 10yrs ago may be visualized by Grafana

## Visuals
See my example showing valves open/closed and temperature_act / temperature_set as tables.

Luckily i do have information about my floor heating system needs. So i could add heating power and heated surface for each room. A simple python script collects the data from JSON, summarizes heating power and heated surface if valves are open. Values are transferred to influxDB regarding a cronjob running every 3 minutes.


## Installation
Having 13 rooms with single temperature control i would have to click super many times in original interface. I wanted to have a quick overview, instead.
## Usage
My dashboard makes use from colour tresholds to indicate wether a room is too cold, ok or overheated.

akt_temp = (parsed_json["result"]["objects"][1]["properties"]["85"]["value"])
soll_temp = (parsed_json["result"]["objects"][2]["properties"]["85"]["value"])
heizt = int((parsed_json["result"]["objects"][3]["properties"]["85"]["value"]))

## Support

## Roadmap

## Contributing

## Authors and acknowledgment


## License
MIT

## Project status
