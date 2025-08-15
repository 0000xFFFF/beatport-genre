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
./beatport-genre.py "Mau P - Gimme That Bounce" -p
```
### Gives:
```
Genre information for: Mau P - Gimme That Bounce
  Matched Title  : Gimme That Bounce Original Mix
  Matched Artists: Mau P
  Genre          : Tech House
  Match Score    : 0.794
```
