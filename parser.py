import json
import math

business_to_square = {}

min_lat = 45.4
max_lat = 45.74
min_long = -74.00
max_long = -73.450

incr_long = (max_long - min_long)/100
incr_lat = (max_lat - min_lat)/100

#squares[day][hour][long][lat], a 2d list representing a grid for every hour of the day for each day of the week
squares = [[[[0 for i in range(100)] for j in range(100)] for h in range(24)] for d in range(7)]

parsed_json = []
parsed_location = []
parsed_filter = []

# take latitude and longitude as input and return its coordinate on the grid
def to_square(lat, long):
	y_square = math.floor((lat - min_lat)//incr_lat)
	x_square = math.floor((long - min_long)//incr_long)
	return [y_square, x_square]
	

# business_info = [id, lat, long]
# return the square the business is in
def place_business(business_info):
	[id, lat, long] = business_info
	return to_square(lat, long)
	
# take a parsed json file and map business check-ins to the map
def map_business(parsed_data):
	for line in parsed_data:
		for dic in line["checkin_info"]:
			key = dic
			val = dic[0]
			
			hour, day = dic.split("-")
			hour = int(hour)
			day = int(day)
			
			lat, long, cat = business_to_square[line["business_id"]]
			
			x,y = to_square(lat, long)
			
			squares[day][hour][x][y] += 1
			
# This method map check-ins from businesses whose industry correspond to filter
def map_filter(filter, parsed_data):
	for line in parsed_data:
		lat, long, cat = business_to_square[line["business_id"]]
		goodLine = False
		for i in range(len(cat)):
			if(filter == cat[i]):
				goodLine = True
		if(not goodLine):
			continue
		for dic in line["checkin_info"]:
			key = dic
			val = dic[0]
			
			hour, day = dic.split("-")
			hour = int(hour)
			day = int(day)
			
			x,y = to_square(lat, long)
			
			squares[day][hour][x][y] += 1
			
	frames_filter("frames_filter/" + filter + "/" + "frames_" + filter + ".csv")
	
# Maps every business to a square on the grid	
def init_business_to_square(location):
	for line in location:
		id = line["business_id"]
		lat = line["latitude"]
		long = line["longitude"]
		categories = line["categories"]
		business_to_square[id] = [lat, long, categories]

#convert squares to latitude and longitude coordinates		
def y_to_lat(y):
	return min_lat + y*incr_lat
	
def x_to_long(x):
	return min_long + x*incr_long

# Creates all the files necessary for the Paraview timeline of the whole week
def frames():
	for d in range(len(squares)):
		for h in range(len(squares[d])):
			filename = "frames/checkin_" + str(d*24 + h) + ".csv"
			with open(filename, 'w') as f:
				f.write("x,y,z,value\n")
				for y in range(len(squares[d][h])):
					for x in range(len(squares[d][h][y])):
						if(squares[d][h][y][x] == 0):
							continue
						x_long = x_to_long(x)+incr_long
						y_lat = y_to_lat(y)+incr_lat
						f.write(str(x_long) + "," + str(y_lat) + ",0," + str(squares[d][h][y][x]) + "\n")

# Creates all the files necessary for the Paraview timeline of the week days						
def frames_week():
	for h in range(24):
		filename = "frames_week/checkin_" + str(h) + ".csv"
		with open(filename, 'w') as f:
			f.write("x,y,z,value\n")
			for y in range(len(squares[1][h])):
				for x in range(len(squares[1][h][y])):
					val_square_week = 0
					for d in range(len(squares)):
						time_of_week = d*24 + h
						if((time_of_week < 137) or time_of_week > 17):
							val_square_week += squares[d][h][y][x]
					if(val_square_week//5 == 0):
							continue
					x_long = x_to_long(x)
					y_lat = y_to_lat(y)		
					f.write(str(x_long) + "," + str(y_lat) + ",0," + str(val_square_week//5) + "\n")

# Creates all the files necessary for the Paraview timeline of the weekend					
def frames_weekend():
	for h in range(24):
		filename = "frames_weekend/checkin_" + str(h) + ".csv"
		with open(filename, 'w') as f:
			f.write("x,y,z,value\n")
			for y in range(len(squares[1][h])):
				for x in range(len(squares[1][h][y])):
					val_square_weekned = 0
					for d in range(len(squares)):
						time_of_weekend = d*24 + h
						if((time_of_weekend >= 137) or time_of_weekend <= 17):
							val_square_weekend += squares[d][h][y][x]
					if(val_square_weekend//2 == 0):
							continue
					x_long = x_to_long(x) + incr_long/2
					y_lat = y_to_lat(y)	+ incr_lat/2
					f.write(str(x_long) + "," + str(y_lat) + ",0," + str(val_square_weekend//2) + "\n")

# Creates all the files necessary for the Paraview timeline according to the filtered insdustry					
def frames_filter(pathname):
	for d in range(len(squares)):
		for h in range(len(squares[d])):
			filename = pathname + str(d*24 + h) + ".csv"
			with open(filename, 'w') as f:
				f.write("x,y,z,value\n")
				for y in range(len(squares[d][h])):
					for x in range(len(squares[d][h][y])):
						if(squares[d][h][y][x] == 0):
							continue
						x_long = x_to_long(x) + incr_long
						y_lat = y_to_lat(y) + incr_lat
						f.write(str(x_long) + "," + str(y_lat) + ",0," + str(squares[d][h][y][x]) + "\n")

with open('checkinQC.json') as data_file:
	for line in data_file:
		parsed_json.append(json.loads(line))
data_file.close()

# Using the file without business categories
with open('businessQC.json') as data_file:
	for line in data_file:
		parsed_location.append(json.loads(line))
data_file.close()

# Using the file with business categories (for the filter)
with open('businessQC_tot.json') as data_file:
	for line in data_file:
		parsed_filter.append(json.loads(line))
data_file.close()

init_business_to_square(parsed_filter)
map_business(parsed_json)
map_filter("Restaurants", parsed_json)