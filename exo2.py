from os import terminal_size
from exo1 import *
while True:
    save_to_mongo(get_renne(),"renne")

    save_to_mongo(get_vlille(),"lille")

    save_to_mongo(get_vlib(),"paris")

    save_to_mongo(get_velov(),"lyon")