# import necessary modules
import datetime

# set necessary variables
now = datetime.datetime.now

# define functions
def dbi(db,level,*args):
    if db['debug_active'] and level <= db['verbosity_level']: # check debug is True and level is okay
        prefixes = {'1': "lvl1!",
                    '2': "lvl2!",
                    '3': "lvl3!"}
        arg_list = []
        for arg in args: arg_list.append(arg)
        output = []
        for i in range(len(arg_list)):
#            print(i)
            if isinstance(arg_list[i],str): # if this arg is a string
#                print("is a string:",arg_list[i])
                output.append(arg_list[i]) # append the arg to a list
                if (i + 1 < len(arg_list)):
                    if (isinstance(arg_list[i + 1],str)): # if next arg is a string
                        pass # do nothing
                    else: # if the next arg isn't a string
                        message = " | ".join(output) # join all the strings and separate them with pipes
                        print("[%s][%s]: %s" % (now().isoformat('T'),prefixes[str(db['verbosity_level'])],message))
                    
            else: # if this arg isn't a string
                try: arg # try executing it
                except: raise Exception("COULDN'T RUN IN DBI!") # otherwise raise an exception
        message = " | ".join(output) # join all the strings and separate them with pipes
        print("[%s][%s]: %s" % (now().isoformat('T'),prefixes[str(db['verbosity_level'])],message))

test = {'bool': True}

def change(my_dict):
    my_dict['bool'] = False

db = {'debug_active': True, 'verbosity_level': 1}
print(test['bool'])
dbi(db,1,"changing...",change(test),"changed!")
print(test['bool'])
