# beatport-genre
scrape song genre from beatport 

## Setup
```sh
./setup-env.sh
./install.sh
```

## Usage
```sh
beatport-genre <song>
```


## Example
### Running:
```console
./beatport-genre.py "Mau P - Gimme That Bounce"
```
### Gives:
```
Genre for 'Mau P - Gimme That Bounce': {'genre': 'Tech House', 'matched_title': 'Gimme That Bounce Original Mix', 'matched_artists': 'Mau P', 'score': 0.794}
```
