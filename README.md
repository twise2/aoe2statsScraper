# aoe2statsScraper
Scrape aoe2 stats to json for some analysis later

## To Use
### Set up the Environment
- Install Conda https://conda.io/projects/conda/en/latest/user-guide/install/index.html
- Set up environment
```
conda env create -f environment.yml
conda activate aoe_elo_notebook
```
- Set up the database
```
python createDB.py
```
- Scrape the data from https://aoe2.net/
```
python scrape.py
```
