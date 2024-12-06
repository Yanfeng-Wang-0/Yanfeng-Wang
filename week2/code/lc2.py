# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: lc2.py
# Description: uses both list comprehensions and conventional loops to filter the data based on rainfall greater than 100 mm and rainfall less than 50 mm
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: uses both list comprehensions and conventional loops to filter the data based on rainfall greater than 100 mm and rainfall less than 50 mm
"""

# Tuple containing monthly rainfall data: (month, rainfall in mm)
rainfall = (('JAN', 111.4),
            ('FEB', 126.1),
            ('MAR', 49.9),
            ('APR', 95.3),
            ('MAY', 71.8),
            ('JUN', 70.2),
            ('JUL', 97.1),
            ('AUG', 140.2),
            ('SEP', 27.0),
            ('OCT', 89.4),
            ('NOV', 128.4),
            ('DEC', 142.2),
           )

# (1) Use a list comprehension to create a list of month,rainfall tuples where
# the amount of rain was greater than 100 mm.
rain_above_100 = [(month, rain) for month, rain in rainfall if rain > 100]
print("Months and rainfall values greater than 100 mm:", rain_above_100)

# (2) Use a list comprehension to create a list of just month names where the
# amount of rain was less than 50 mm.
rain_below_50 = [month for month, rain in rainfall if rain < 50]
print("Months with rainfall less than 50 mm:", rain_below_50)

# (3) Now do (1) and (2) using conventional loops

# Initialize an empty list to store months with rainfall greater than 100 mm
rain_above_100 = []
# Loop through each month and rainfall in the rainfall tuple
for month, rain in rainfall:
    if rain > 100:  # Check if rainfall is greater than 100 mm
        rain_above_100.append((month, rain))  # Add month and rainfall to the list
print("Months and rainfall values greater than 100 mm:", rain_above_100)

# Initialize an empty list to store months with rainfall less than 50 mm
rain_below_50 = []
# Loop through each month and rainfall in the rainfall tuple
for month, rain in rainfall:
    if rain < 50:  # Check if rainfall is less than 50 mm
        rain_below_50.append(month)  # Add month to the list
print("Months with rainfall less than 50 mm:", rain_below_50)
