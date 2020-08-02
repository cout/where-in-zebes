default: all

RandomMetroidSolver:
	git clone https://github.com/theonlydude/RandomMetroidSolver.git

items.json: RandomMetroidSolver
	./gen_items_json.py

locations.json: RandomMetroidSolver
	./gen_locations_json.py

seeds.json: seeds/*.txt
	./gen_seeds_json.py

all: items.json locations.json seeds.json
