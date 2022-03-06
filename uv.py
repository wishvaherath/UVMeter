#Wishva Herath
from urllib.request import urlopen
import argparse 
import datetime
from datetime import datetime
import sys


#ARPANSA data link.
link = "https://uvdata.arpansa.gov.au/xml/uvvalues.xml"
data = ""

#ascii map modified from https://ascii.co.uk/art/australia
mapp = r"""

                    _,__        .:
               DDD <*  /        | \
               .-./     |.     :  :,
              /           '-._/     \_
             /                '       \
           .'      UV Radiation        *: BBB
        .-'            of               ;
        |           AUSTRALIA           |
        \                              /
         |                            /
     PPP  \*        __.--._         */ SSS
           \     _.'    AAA \*.      *| CCC
           >__,-'             \_/*_.-'
                                MMM
                                :--,
                                 '/
"""


p = argparse.ArgumentParser(description="Shown the current UV index for the given location. \n UV observations courtesy of ARPANSA")
p.add_argument("--list", action="store_true", help="List all locations together with their operational status")
p.add_argument("--all", action="store_true", help="Show data for all locations.")
p.add_argument("--detailed", action="store_true", help="Show all available stats. Use with --loc")
p.add_argument("--loc", action="store", type=str, help="Location for the UV readout. (Use --list for a list of locations).")
p.add_argument("--map", action="store_true", help="Shows the UVR indexes of the capital cities in Australia.")
args = p.parse_args()

def colored(r, g, b, text):
    """

    color code from https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal; answer by L D

    > colored_text = colored(255, 0, 0, text)

    """
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

extreme = colored(153,51,51,"!!!EXTREME!!!")
very_high = colored(204,0,0,"!!VERY HIGH!!")
high = colored(255,102,0, "!HIGH!")
moderate = colored(255,153,102, "MODERATE")
low = colored(102,255,51, "LOW")

def speed_check():
    try:
        f = open("uv.tmp","r")
        dt = f.read()
        f.close()
        old_time = datetime.strptime(dt, '%Y/%m/%d %H:%M:%S')
        now = datetime.utcnow()
        gap = now - old_time
        # print(gap.seconds)
        if round(gap.seconds) < 5:
            print("Please allow for at least 5 seconds between subsequent calls (Last call was", gap.seconds, "second(s) ago. Exiting...")
            return False
        else:
            return True

    except:
        return True

def readurl(link):
    """
    reads a given url 
    """

    #[debug]
    # f = open("uvvalues.xml")
    # data = f.read()
    if speed_check():
        global data
        if data == "":
            print("loading data ...")
            f_link = urlopen(link)
            data = f_link.read()
            data = data.decode('utf-8')

            f = open("uv.tmp","w")
            f.write(datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S'))
            f.close()

            now = datetime.utcnow()

        return(data)
    else:
        sys.exit(1)


def extract_xml(string):
    """

    extract value between > x <
    I was too lazy to parse it properly

    """

    return string.split(">")[1].strip().split("</")[0].strip()


def classify_uv(index):
    i = float(index)
    if i < 2:
        return low
    elif i <= 5:
        return moderate
    elif i <= 7:
        return high
    elif i <= 10:
        return very_high
    else:
        return extreme

def time_delta(utcdatetime):
    # In [3]: tt = datetime.datetime.strptime(t, '%Y/%m/%d %H:%M')

    now = datetime.utcnow()
    previous = datetime.strptime(utcdatetime, '%Y/%m/%d %H:%M')

    gap = now - previous
    return (round(gap.seconds/60))


def search_loc(loc):
    read = False
    count = 0

    data = readurl(link)
    name = ""
    index = ""
    time = ""
    date = ""
    fulldate = ""
    utcdatetime = ""
    status = ""

    for line in data.split("\n"):
        if read:
            if "<name>" in line:
                name = extract_xml(line)
            if "<index>" in line:
                index = extract_xml(line)
            if "<time>" in line:
                time = extract_xml(line)
            if "<date>" in line:
                date = extract_xml(line)
            if "<utcdatetime>" in line:
                utcdatetime = extract_xml(line)
            if "<status>" in line:
                status = extract_xml(line)
                break

                # read = False

        if "<location" in line:
            if line.strip().split('id="')[1].strip().split('">')[0].strip() == loc:
                read = True
                continue
    return (name,index,time,date,fulldate,utcdatetime,status)



if args.list:
    locations = []
    status = []
    data = readurl(link)
    # print(data)
    for line in data.split("\n"):
        if "<location" in line:
            # too lazy to parse xml properly
            # print(line.strip())
            locations.append(line.strip().split('id="')[1].strip().split('">')[0].strip())

        if "<status>" in line:
            # status.append(line.strip().replace("<status>","").replace("</status>",""))
            status.append(extract_xml(line.strip()))


    print("----------------------------------")
    print("UV meter locations")
    print("----------------------------------")
    for (l,s) in zip(locations,status):
        print("| ", l, " [",s,"]" )

    print("----------------------------------")


if args.all:
    locations = []
    status = []
    data = readurl(link)
    # print(data)
    for line in data.split("\n"):
        if "<location" in line:
            # too lazy to parse xml properly
            # print(line.strip())
            locations.append(line.strip().split('id="')[1].strip().split('">')[0].strip())

        if "<status>" in line:
            # status.append(line.strip().replace("<status>","").replace("</status>",""))
            status.append(extract_xml(line.strip()))

    index_dict = {}
    # mapp = colored(0,204,102,mapp)
    # print(mapp)

    sys.stdout.write("\033[F") # Cursor up one line
    for city in locations:
        # print("calling", city)
        name,index,time,date,fulldate,utcdatetime,status = search_loc(city)
        # index_dict[city] = search_loc(city)

        print(colored(255,255,255,"UVR in"), city, "is"  ,index, "[", classify_uv(index), "]", "Measured", time_delta(utcdatetime), "min ago.")
    print("UV observations courtesy of ARPANSA.")










if args.loc:

    name,index,time,date,fulldate,utcdatetime,status = search_loc(args.loc)
    # print(name, index, classify_uv(index), date, time , status)
    if args.detailed:

        sys.stdout.write("\033[F") # Cursor up one line
        print(colored(255,255,255,"|========================================|"))
        print(colored(255,255,255,"| Classification:"), classify_uv(index))
        print("| UV Index:", index)
        print("| Location:", args.loc)
        print("| Date:", date)
        print("| Time:", time)
        print("| UTCdatetime:", utcdatetime)
        print("| Measured", time_delta(utcdatetime) , "minutes ago")
        print("| Status:", status)
        print("| UV observations courtesy of ARPANSA.")
        print("|========================================|")
    else:
        # print("UVR level in", colored(0,153,255, args.loc), "taken", time_delta(utcdatetime)   , "min ago is", index,  "[", classify_uv(index), "]")


        sys.stdout.write("\033[F") # Cursor up one line

        print(colored(255,255,255,"UVR ="), index, "[", classify_uv(index), "]")
        print("Measured", time_delta(utcdatetime)   , "min ago.")
        print("UV observations courtesy of ARPANSA.")


if args.map:
    sys.stdout.write("\033[F") # Cursor up one line

    city_code = ["AAA", "BBB", "CCC", "DDD", "MMM", "PPP", "SSS"]
    cities = ["Adelaide", "Brisbane", "Canberra", "Darwin", "Melbourne", "Perth", "Sydney"]
    city_dict = dict(zip(cities, city_code))
    index_dict = {}
    # mapp = colored(0,204,102,mapp)
    # print(mapp)
    for city in cities:
        # print("calling", city)
        name,index,time,date,fulldate,utcdatetime,status = search_loc(city)
        index_dict[city] = index
        mapp = mapp.replace(city_dict[city], colored(255,0,0,index))

    print(mapp)







