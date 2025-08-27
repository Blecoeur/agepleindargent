# AGEPleinDargent

## tech stack 
- React
- Tailwindcss
- Fastapi
- postgresql
- Docker compose

## App description
The app allows to view transactions from many Electronic Payment Terminals in an event.

An event consists of a name, a beginning time, an end time, and some selling points. 
A selling point consist of a list of EPTs, a location, and a name.
A transaction is a record of a purchase made at a selling point using an EPT. It includes details such as the amount, timestamp and the last 4 digits of the card used.

## v0 Features
- Create an event, selling points and EPTs
- Modify them
- Delete them
- Import transactions from a CSV file. For now, just use mock data, but ensure that it will be easy to replace with real data later.
    1. It's possible to have more than one CSV from differents EPT providers, worldline, sumup,... Each CSV has its own format, so we need to parse them differently. You need to include the possibility to choose the parser when importing a CSV. For now, just implement one parser with mock data.
- View an event : 
    1. View 1 : Summaries 
        - List selling points
        - For each selling point, list EPTs and generic data
    2. View 2 : Event timeline in a map view.
        - Display the total amount of transactions over time, in a map. The selling points are represented as circles, with a size proportional to the total amount of transactions at that selling point (up to this moment of the time).
        - You can look at [test.html](test.html) for an example of how to do it.

## v1 Features
- Add subevents (like a concert in a festival) in the event. It consists of a name, a beginning time, an end time, and a location.
- Display the subevents in the timeline view
- Add entry points (like the entrance of the festival) in the event. It consists of a name, a location.
- Add entries to the event. It consists of a timestamp, an entry point, and a ticket type (like "1 day pass", "full pass", etc). 
- View entries in the timeline view
- Summaries export (CSV, PDF)