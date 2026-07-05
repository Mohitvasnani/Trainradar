from shapely.geometry import LineString
line = LineString([(0,0), (10,0), (10,10)])

print(f"lenght of line {line.length}")
halfway = line.interpolate(10)
print(f"half {halfway}")


# And a quarter of the way (distance = 5 of 20).
quarter = line.interpolate(5)
print(f"Point at distance 5 (quarter): {quarter}")

# You can also ask by FRACTION instead of distance, with normalized=True.
# 0.5 means "halfway", 0.75 means "three-quarters".
three_quarters = line.interpolate(0.75, normalized=True)
print(f"Point at 75% along the line: {three_quarters}")