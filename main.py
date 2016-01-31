import xml.etree.ElementTree
from decimal import Decimal

#Assumption of maximum of 2 changes

__author__ = 'randeep'

STATION_FILE_PATH = 'Stations.xml' #Path to stations.xml
LINES_FILE_PATH = 'lines.xml' #Path to lines.xml
ZONES_FILE_PATH = 'zones.xml' #Path to zones.xml
ACCEPTED_COINS = ['1p', '2p', '5p', '10p', '20p', '50p', '£1', '£2']
PRICE_VALUE = [0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.00, 2.00]

def load_xml_files():
    """
    Returns xml data as stored data using the xml.etree.ElementTree module
    """
    station_element_tree = xml.etree.ElementTree.parse(STATION_FILE_PATH) #Station XML file loaded
    lines_element_tree = xml.etree.ElementTree.parse(LINES_FILE_PATH) #lines XML file loaded
    zone_element_tree = xml.etree.ElementTree.parse(ZONES_FILE_PATH) #zones XML file loaded

    global station_objects #Public station objects
    global lines_objects #Public line objects
    global zone_objects #Public zone objects

    #Set objects to correspond with the files
    station_objects = station_element_tree.getroot()
    lines_objects  = lines_element_tree.getroot()
    zone_objects = zone_element_tree.getroot()
    return


def station_exists(station_name):
    """
    Returns boolean to check if station exists inside station_objects
    """
    for station in station_objects: #Loop through station objects
        name = station.attrib['id'] #Check the attribute 'id' for the station
        if name.lower() == station_name.lower(): #If the name is inside the station_ojects return true
            return True
    return False


def get_stations(line):
    """
    Returns all station names on a line
    """
    stations = [] #Station names to return
    for lines in lines_objects: #Loop through line objects
        if lines.attrib['id'] == line: #If the line name is equal to the line argument
            for xml_element in list(lines):
                if 'part' in xml_element.tag:
                    for station in list(xml_element):
                        if 'station' in station.tag:
                            station_name = station.text
                            station_name = station_name.replace('"','')
                            stations.append(station_name)
                elif 'station' in xml_element.tag: #If tag contains station then the text contains a station name
                    station_name = xml_element.text #Format the string
                    station_name = station_name.replace('"', '') #Format the string
                    stations.append(station_name) #Add station inside list
    return stations

#Can the person travel from station1 to station2 and switch lines to target_line
def can_travel(station1, station2, target_line):
    """
    Returns false if station2 is not on target line and true if both station
    lines intersect
    """
    lines1 = find_lines_for_station(station1) #All line1
    lines2 = find_lines_for_station(station2) #All line2

    if target_line not in lines2: #If target lines are not in second station then return false
        return False

    #If the 2 lines intersect at all then return true
    for line1 in lines1:
        for line2 in lines2:
            if line1 == line2:
                return True
    return False


def find_lines_for_station(station_name):
    """
    Returns all the lines the station is on
    """
    for stations in station_objects: #Loop through stations
        if(station_name.lower() == stations.attrib['id'].lower()): #If station_name inside station_objects
            #String formatting
            station_raw_string = stations.find('Line').text #Get Line value
            station_raw_string = station_raw_string.replace(" ", "")
            station_raw_string = station_raw_string.replace("[", "")
            station_raw_string = station_raw_string.replace("]", "")
            #End string formatting
            station_list = station_raw_string.split(',') #Split the string by ','
            return station_list #Return station list
    return


def get_position_on_line(station_string, line):
    """
    Returns the index of station on a certain line
    """
    for lines in lines_objects: #Loop through line_objects
        if lines.attrib['id'] == line: #Loop through 'line'
            for station in list(lines):
                if station_string and station_string == station.text and 'station' in station.tag: #If station tag is station
                    station_tag = station.tag #Format string for integer
                    station_tag = station_tag.replace("station", "") #Format string for integer
                    return int(station_tag) #Return the integer
    return -1

def get_distance_on_line(start_station, target_station, line):
    """
    Returns the distance between two stations on a certain line
    """
    return abs(get_position_on_line(start_station, line) - get_position_on_line(target_station, line)) #Abs non negative


def calculate_route(start_station, end_station):
    """
    Returns the route between two stations and outputs a readable output
    """
    start_lines = find_lines_for_station(start_station) #Start Lines possible starting points
    target_lines = find_lines_for_station(end_station) #Target lines possible finish points

    lowest_journey_distance = 1000 #Lowest journey distance is a extreme
    lowest_journey = [] #Lowest Journey element

    for start_line in start_lines: #Loop through all start_lines (Do not limit start lines)
        if(start_line in target_lines): #If start line is equal to the target line already then return a 1 way route
            return [start_station, start_line + " Line", end_station]

        for target_line in target_lines: #Loop through target_lines (Do not limit target lines)
            for first_station in get_stations(start_line): #Gets the start_line stations and goes through all of them
                if can_travel(start_station, first_station, target_line): #If the startStation to the firstStation can be travelled and the first_station has the target_line
                    distance_map = [0, 0] #2 Element distance map
                    distance_map[0] = get_distance_on_line(start_station, first_station, start_line) #Distance 1 first train
                    distance_map[1] = get_distance_on_line(first_station, end_station, target_line) #Distance 2 second train
                    total_distance = sum(distance_map) # Calculate total_distance
                    if total_distance < lowest_journey_distance: #If total distance is less than lowest_journey_distance
                        lowest_journey = [start_station, start_line + " Line", first_station, target_line + " Line", end_station] #Set lowest journey
                        lowest_journey_distance = total_distance #lowest_journey_distance is set
                    continue
    return lowest_journey #Returns lowest_journey


def get_zone_change_price(first_zone, second_zone):
    """
    Returns the price between two zones
    """
    for zone in zone_objects: #Loop through Zones
        if('Zone'+str(first_zone) == zone.attrib['id']): #If Zone{ID} inside Zone
            for children in list(zone): #All children inside zone object
                if(children.text and 'Zone' in children.tag and children.tag == 'Zone'+str(second_zone)): #If the zone matches the second zone
                    zone_text = children.text.replace(" ", "") #Format string for decimal
                    double = Decimal(zone_text) #Get decimal
                    return double #Return decimal
    return -1


def calculate_price(journey):
    """
    Returns price for one step and two step journeys
    """
    if len(journey) == 3:
        first_zone = get_zone(journey[0])
        second_zone = get_zone(journey[2])
        return get_zone_change_price(first_zone, second_zone)
    else:
        first_zone = get_zone(journey[0])
        second_zone = get_zone(journey[2])
        third_zone = get_zone(journey[4])
        return get_zone_change_price(first_zone, second_zone) + get_zone_change_price(second_zone, third_zone)

def get_zone(station_name):
    """
    Returns zone for station name
    """
    for stations in station_objects: #Loop through stations
        if(station_name.lower() == stations.attrib['id'].lower()): #If station_name inside station_objects
            #String formatting
            station_zone = stations.find('Zone').text #Get Line value
            return int(station_zone) #Get integer
    return -1

def handle_price_input(price_input): #Handle price input from accepted coins
    """
    Returns ticket price as decimal integer
    """
    index = 0 #Index of the coin string
    for accepted_coins in ACCEPTED_COINS: #Loop through accepted_coins
        if accepted_coins.lower() == price_input.lower(): #If price input contains accepted coins
            return Decimal(format(PRICE_VALUE[index], '.2f')) #Return a 2 decimal place number
        index += 1 #Increase index
    return 0 #Return 0 if price input is not found

def main():
    """
    Uses station input, calculates route and issues ticket with price and change due
    """
    load_xml_files() #Load xml files
    start_station = '' #Start station
    target_station = '' #Target station

    #Obtain start station
    while(True):
        start_station = input("Enter start station: ")
        if(station_exists(start_station) == False): #If station does not exist then re-enter station
            print('There is no station called '+start_station+'. Please re-enter the start station.')
            continue
        break #Break if station exists

    #Obtain final station
    while(True):
        target_station = input("Enter target station: ")
        if(station_exists(target_station) == False): #If station does not exist then re-enter staiton
            print('There is no station called '+target_station+'. Please re-enter the destination station.')
            continue
        #start and target station cannot be equal
        if target_station.lower() == start_station.lower():
            print('The start station & the target station cannot be the same. Please re-enter the destination station.')
            continue

        break

    journey = calculate_route(start_station, target_station) #Calculate the route

    if (len(journey) == 0): #If len of journey is 0 then do not continue
        print('Nothing found. Error')
        return

    final_price = calculate_price(journey) #Constant price
    price = final_price #Price which is changed

    print(journey) #Prints out journey
    print("Total price of this ticket is: £"+str(price)+"p") #Prints out total price

    while price >= 0: #While price is greater than 0
        print("Total to pay for ticket: "+str(price))
        price_input = input("Add coins (Only accepting: 1p, 2p, 5p, 10p, 20p, 50p, £1, £2): ") #Get price input
        processed_price = handle_price_input(price_input) #Process price_input into a 2d decimal

        price -= processed_price #Minus value
        if processed_price == 0: #If the value to minus is 0 then the coin entered is invalid
            print("The only coins which are accepted are: 1p, 2p, 5p, 10p, 20p, 50p, £1, £2. Try again")
            continue
        if price <= 0: #If price <= 0 then break loop and show change due
            print("You have recieved "+str(abs(price))+ "p change.")
            print("You have purchased the ticket from "+start_station+" to "+target_station+" for "+str(final_price)+".")
            break

    print("Ticket: "+str(journey)+" Price: "+str(final_price)) #Print ticket with journey and price
    return

main()