# Footballes value
The goal of this project is to collect football players data for the major 5
European Leagues from the platform
[Transfermarkt](https://www.transfermarkt.com/).
The data is than used to build data analysis and visualisation tools. 

### Strategy:
- Build an ETL pipeline to scrape Data from the platform, normalize and store it in a database
- Write a data aggregation framework to perform data analysis (e.g., Average cost of players in each league, Player’s nationality frequency, etc.)
- Build web application to visualize aggregated results as interactive dashboard
- Application deployment on Docker container
- CI/CD: Github actions and webhook to test PRs and deploy on server
### Tools:
- Python [requests](https://docs.python-requests.org/en/master/) and [Beautifulsoup](https://www.crummy.com/software/BeautifulSoup/) to collect the data and SQLite to store them
- Data acquisition pipeline is automatized with [Prefect](https://www.prefect.io/)
- Data validatation is ensured by [Great Expectations](https://greatexpectations.io/)
- Flask to build the web application to enable the Webhook
- Dash to build the dashboard
### Data:
Raw data will be stored in a single table including the following information
| players_raw             | description                     |
|-------------------------|---------------------------------|
| name                    | name and surname of the player  |
| team                    | player's team for that season   |
| league                  | league where the players plays  |
| role                    | role of the player              |
| date_of_birth           | date of birth                   |
| age                     | age                             |
| height                  | player's height                 |
| foot                    | right or left foot              |
| joined                  | data the player joind the team  |
| contract_expires        | date when contract ends         |
| market_value            | market value of the player      |
| nationality             | coutry of origin                |
| nation_flag_url         | link to image with country flag |
| player_transfermarkt_id | unique id from transfermarkt    |
| player_picture_url      | url to player image             |
| updated_on              | data when data was collected    |
| season                  | season                          |
### Installation
The following instructions explain how to pull the data from transfermarkt and
run the dashboard:
- Clone the repo:
```
git clone https://github.com/mrvaita/footballers_value
cd footballers_value
```
- create virtual environment and install dependencies:
```
python3 -m venv
. venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```
- populate database (I will take some time)
```
export DATABASE_URL=sqlite:////path/to/football_players.sqlite
python populate_db.py
```
- run the application
```
gunicorn --bind 0.0.0.0:8000 wsgi:server
```
You can now navigate with your web browser to http://localhost:8000
#### Using Docker
```
git clone https://github.com/mrvaita/footballers_value
cd footballers_value
docker build -t tmarkt .
docker run --name footballers -p 8000:5000 --rm tmarkt:latest
```
Note that when you run the docker container the database will be automatically
populated and the database update script will be executed to pull new data
every year.
You can add the flag `-d` to the docker run command to execute the container in
the background.
In case you are using a Raspberry Pi, please build the docker image using the
command `docker build -t tmarkt -f DockerfilePi .`. This specific dockerfile
will use [PiWheels](https://www.piwheels.org/) to install the dependencies.
If the installation is successfull you can visit the dashboard
http://localhost:8000.

### Architecture
You can see more details about the project in the included [pdf]().
