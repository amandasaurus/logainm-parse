logainm-csvs/all-of-logainm.csv: logainm-csvs.zip
	-rm -rf ./logainm-csv/
	aunpack logainm-csvs.zip

convex-hulls.csv: group-items.py
	python group-items.py ./logainm-csvs/ ./convex-hulls.csv

