#-------------------------------------------------#
# Title: Database MailRoom
# Dev:   LDenney
# Date:  January 1, 2018
# ChangeLog: (Who, When, What)
#   Laura Denney, 10/11/18, Created MailRoom Part 1 File
#   Laura Denney, 10/12/18, Modified MailRoom Part 1 File
#   Laura Denney, 10/12/18, Started Part 2
#   Laura Denney, 10/12/18, Finished Part 2
#   Laura Denney, 10/31/18, Started MailRoom Part 3
#   Laura Denney, 11/7/18, Started MailRoom Part 4
#   Laura Denney, 12/7/18, Started Object Oriented Mail Room
#   Laura Denney, 12/17/18, Added Saving / Loading Functionality
#   Laura Denney, 1/1/19, Started Functional Programming MailRoom
#   Laura Denney, 5/10/19, Started Database MailRoom
#-------------------------------------------------#

#importing models, logging, datetime, peewee
from mailroom_populate import *

#file handling help
import os

####################################################
####################################################

#Non-class variables and functions

dh = Database_Handler()

main_prompt = '''
What would you like to do today?
1) Send a Thank You
2) Create a Report
3) Send letters to everyone
4) See projections for matching contributions
5) Update or Remove a Donor in the system
6) Quit
Please choose the number of your choice >> '''

thank_you_prompt = '''
You have chosen to Send a Thank You.
1) See List of Current Donors
2) I'm Ready to Thank a Donor
3) Quit this submenu
Please choose the number of your choice >> '''

update_prompt = '''
You have chosen to Update or Remove a Donor.
1) Update Donor information
2) Update Donation amount
3) Remove a Donor and all their Donations
4) Quit this submenu
Please choose the number of your choice >>
'''

yes_no_prompt = '''
1) Yes
2) No
Please choose the number of your choice >>
'''

#************Map function
def map_projection(multiplier=0, min_donation=0, max_donation=0, projection_list=None):
    if min_donation and max_donation:
        filtered_list = list(filter(lambda x: x >= min_donation and x <= max_donation, projection_list))
    elif min_donation:
        filtered_list = list(filter(lambda x: x > min_donation, projection_list))
    elif max_donation:
        filtered_list = list(filter(lambda x: x < max_donation, projection_list))
    new_donations = list(map(lambda x: x * multiplier, filtered_list))
    return new_donations

def projections():
    projection_list = dh.projection_query()
    str_projections = '''
Current total donations to our cause: ${:.2f}
Your contribution if doubling contributions under $100: ${:.2f}
Your contribution if tripling contributions over $50: ${:.2f}
Your contribution if quadrupling contributions between $50 and $100: ${:.2f}
'''
    print(str_projections.
          format(
            sum(projection_list),
            sum(map_projection(2,max_donation = 100, projection_list = projection_list)),
            sum(map_projection(3,min_donation = 50, projection_list = projection_list)),
            sum(map_projection(4,50,100, projection_list = projection_list))
            )
          )

def send_thank_you():
    while True:
        try:
            response = input(thank_you_prompt)
            if sub_choice_dict[response]() == 'quit':
                print("\nYou have chosen to leave this submenu.")
                break
        except KeyError:
            print("\nThat is not a valid selection. Please choose 1, 2, or 3.")

def send_letters():
    print("\nYou have chosen to send letters to everyone.")
    total_letters_sent = send_letters_per_donor()
    print(f"\nA total of {total_letters_sent} letters have been successfully sent to our donors.")
    print("A copy of those letters are now saved in your current directory.")

def send_letters_per_donor():
    NAME = 0
    SUM = 1

    total_letters = 0
    letter_list = dh.letter_query()
    for each_donor in letter_list:
        donor = each_donor[NAME].title()
        #Name formatting for one word names like 'Cher' vs normal full names
        first_last = donor.split(" ")
        if len(first_last) == 1:
            first = first_last[0]
            last = ""
        else:
            first = first_last[0]
            last = first_last[1]
        total_letters += send_email(donor, each_donor[SUM], "{}_{}_{}.txt".format(first, last, date.today().isoformat()))
    return total_letters

def quit(donor=0):
    return 'quit'

def print_list():
    print(dh.get_list())

def validate_yes_no(name):
    while True:
        try:
            yesno = input(yes_no_prompt)
            if yes_no_dict[yesno](name)  == 'quit':
                return False
            else:
                print("Thank you, we will add them to our system")
                dh.add_donor(name)
                return True
        except KeyError:
            print("\nThat is not a valid selection. Please choose 1 or 2.")

def thank_a_donor():
    try:
        name = input("\nPlease enter the full name of the donor you would \
like to thank: ").lower()
        if not dh.is_current_donor(name):
            print("\n{} is not a current donor, would you like to add \
them as a new donor?\n".format(name.title()))
            #ask_yes_no returns False if no
            if not validate_yes_no(name):
                return
        else:
            print("\n{} is a current donor, we will update their donations."
                  .format(name.title()))
        donation = validate_donation()
        dh.add_donation(donation, name)
        print("The email you are sending is as follows:")
        print(send_email(name.title(), donation))
        print("You have successfully sent a Thank You to {}.".format(name.title()))
    except Exception as e:
        logger.info(e)

def validate_donation():
    while True:
        try:
            donation = input("How much money did they donate? (type 100 for $100) >> ")
            num = float(donation)
        except ValueError:
            print("\nERROR: Invalid donation amount entered. Please enter valid number.")
        else:
            return num

#modified to either print to screen or disk
def send_email(donor, amount, dest = 0):
    fstring =f'''
    Dear {donor},

    We would like to thank you for your generous donation
    of ${amount:.2f}. It will be put to great use!

    Thank you!
    <3 The MailRoom
    '''
    if not dest:
        return fstring
    else:
        with open(dest, 'w') as outfile:
            outfile.write(fstring)
        return 1


def create_report():
    NAME = 0
    SUM = 1
    COUNT = 2

    print("\nYou have chosen to Create a Report.")
    report_list = dh.report_query()
    report = '''
Donor Name                | Total Given | Num Gifts | Average Gift
------------------------------------------------------------------'''
    strformat = '\n{:<26}${:>13.2f}{:^12}${:>13.2f}'
    for donor in report_list:
        donation_average = donor[SUM]/donor[COUNT]
        report +=  strformat.format(donor[NAME].title(), donor[SUM],
                                    donor[COUNT], donation_average)
    return report

def print_report():
    print(create_report())

def check_if_database():
    if not os.path.isfile("mailroom.db"):
        first_run()

#Main Menu options for user
main_choice_dict = {
    "1": send_thank_you,
    "2": print_report,
    "3": send_letters,
    "4": projections,
#    "5": update_remove_donor,
    "6": quit
}

#Send Thank You Sub Menu options for user
sub_choice_dict = {
    "1": print_list,
    "2": thank_a_donor,
    "3": quit
}

#Update Remove Donor submenu
sub_update_remove = {
    "1":
    "2":
    "3":
    "4": quit
}

#yes no dict
yes_no_dict = {
    "1": dh.add_donor,
    "2": quit
}

#Main menu to prompt user
def prompt_user():
    check_if_database()
    while True:
        try:
            response = input(main_prompt)
            if main_choice_dict[response]() == 'quit':
                print("\nYou have chosen to quit. Have a good day!")
                break
        except AttributeError:
            print("\nA saved list of donors was found, please load the saved list.")
        except KeyError:
            print("\nThat is not a valid selection. Please choose option 1 - 6.")
        except FileNotFoundError:
            print("\nNo saved list of donors found, please work with current list.")
##########################################################

if __name__ == '__main__':
    prompt_user()



