

HOW TO RUN

1. navigate to the root folder: case_km/
2. create venv: python3.13 -m venv venv
3. activate venv: source venv/bin/activate  (for mac)
4. install requirements: pip install -e .
5. run application by writing the following (in any folder as long as venv is active): go-nogo
6. open static HTML file to view result. Link: http://127.0.0.1:5500/static/index.html



ASSUMPTIONS

Beam sector: the case defines beam sea as 30–150°. This is assumed to also cover the mirrored sector 210–330° on the opposite side of the vessel.
Boundary angles: the boundary angles (30°, 150°, 210°, 330°) are treated as head/stern, not beam. Beam is strictly between these values.
Angle normalisation: vessel-relative wave angles are normalised to [0°, 360°) to handle cases where subtraction yields negative values.
Timestep interval: the API is assumed to return one timestep per hour, so GO/NO-GO counts are reported directly as hours.
Operator responsibility: this tool reports objective wave conditions and GO/NO-GO status at each timestep. The ultimate operational decision rests with the operator.
Use of JavaScript: Minimal JavaScript was used to render data for visualisation 



DESIGN CHOICES

Module seperation: the codebase is split into three modules with distinct responsibilities: case.py for data retrieval and decision logic, db.py for database operations, and export.py for frontend output. This makes it straightforward to locate where each concern is handled.
Visualisation: Visualisation logic is handled in Python using Plotly, which exports directly to JSON. JavaScript is used only to load and render the data, keeping the frontend layer thin.
Two database tables: raw timeseries data and aggregated statistics are stored in separate tables (data and stats) to keep raw and derived data distinct.
Database reset on each run: the database is cleared at the start of every run since retaining historical forecast runs has no value for this use case.
Numpy for wave data: wave direction and height are stored as a (2, N) numpy array rather than separate lists, which gives cleaner column-wise syntax for the decision logic.



ADDITIONAL FUNCTIONALITES THAT COULD HAVE BEEN NICE TO HAVE (TODO)
- App should say which longitude and lattitude are applied
- At the top of the graph it should be a current-status showing if the current weather allows for GO or NO-GO. 
  If GO, it should say how many GO hours are estimated based on the forecast.
- For the Longest GO window, it should say when the window starts

