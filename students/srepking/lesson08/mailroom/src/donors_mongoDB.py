import logging
from pymongo import ReturnDocument
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Group:
    """This Class will be used to query the database and return the results
    of the required queries."""

    def __init__(self, client_path):
        self.db = client_path

    def search(self, person):
        """Return None if donor is not in database."""
        try:
            logger.debug('Search for donor.')
            result = self.db.find_one({'donor': person})
            if result is None:
                logger.debug('Could not find the donor.')
                return result
            else:
                logger.debug(f'Found {result["donor"]}')
                return result['donor']

        except Exception as e:
            logger.debug(f'Error searching for = {person}')
            logger.debug(e)
        finally:
            print(f'All done searching donors for {person}.')

    def print_donors(self):
        # This prints the list of donors

        try:
            donor_list = []
            for doc in self.db.find():
                donor_list.append(doc['donor'])
                print(doc['donor'])

        except Exception as e:
            logger.debug(f'Error printing donors.')
            logger.debug(e)
            logger.debug('Failed to print a list of donors.')
        finally:
            logger.debug('database closes')
            return donor_list

    def summary(self):
        """Create a new dictionary with Total, number of donations,
        and average donation amount"""
        donor_summary = {}
        individual = Individual(self.db)

        try:
            for doc in self.db.find():
                donor_summary[doc['donor']] = \
                    [individual.sum_donations(doc['donor']),
                     individual.number_donations(doc['donor']),
                     individual.avg_donations(doc['donor'])]

        except Exception as e:
            logger.debug(f'Error creating database summary.')
            logger.debug(e)
            logger.debug('Failed to iterate through database '
                         'to create a summary.')
        finally:
            logger.debug('database closes')
            return donor_summary

    @staticmethod
    def column_name_width(donor_summary):
        # creates a list of keys
        name_list = list(donor_summary.keys())
        name_wi = 11  # Establish minimum column width
        for i in name_list:
            if len(i) > name_wi:
                name_wi = (len(i))  # width of name column
        return name_wi

    @staticmethod
    def column_total_width(donor_summary):
        tot_wi = 12
        for name, summary in donor_summary.items():
            if len(str(summary[0])) > tot_wi:
                # width of total column
                tot_wi = (len(str(summary[0]))) + 3
                # width of number of donations column
        return tot_wi

    @staticmethod
    def column_average_width(donor_summary):
        ave_wi = 12
        for name, summary in donor_summary.items():
            if len(str(summary[2])) > ave_wi:
                # width of total column
                ave_wi = (len(str(summary[2]))) + 3
                # width of number of donations column
        return ave_wi

    @staticmethod
    def column_number_width(donor_summary):
        num_wi = 12
        for name, summary in donor_summary.items():
            if len(str(summary[1])) > num_wi:
                # width of total column
                num_wi = (len(str(summary[1]))) + 3
                # width of number of donations column
        return num_wi

    @staticmethod
    def sort_list(donor_summary):
        list_sorted = sorted(donor_summary,
                             key=donor_summary.__getitem__, reverse=True)
        return list_sorted

    def report(self):
        """Return a report on all the donors"""
        donor_summary = self.summary()
        name_wi = Group.column_name_width(donor_summary)
        tot_wi = Group.column_total_width(donor_summary)
        num_wi = Group.column_number_width(donor_summary)
        ave_wi = Group.column_average_width(donor_summary)

        list_sorted = Group.sort_list(donor_summary)

        rows = ['\n''A summary of your donors donations:',
                f"{'Donor Name':{name_wi}}| {'Total Given':^{tot_wi}}| "
                f"{'Num Gifts':^{num_wi}}| {'Average Gift':^{ave_wi}}",
                f"{'-':-^{(name_wi+tot_wi+ave_wi+num_wi+8)}}"]

        for key in list_sorted:
            temp = donor_summary[key]
            rows.append(f"{key:{name_wi}}${temp[0]:{tot_wi}.2f}"
                        f"{temp[1]:^{num_wi}}   "
                        f"${temp[2]:>{ave_wi}.2f}")
        return '\n'.join(rows)

    def letters(self):
        """Send letters to everyone base on their last donation amount."""
        individual = Individual(self.db)

        try:
            for doc in self.db.find():
                logger.debug(f'{doc["donor"]}')
                letter = f'Dear {doc["donor"]}, ' \
                         f'thank you so much for your ' \
                         f'last contribution of ' \
                         f'${individual.last_donation(doc["donor"]):.2f}! ' \
                         f'You have contributed a total of $' \
                         f'{individual.sum_donations(doc["donor"]):.2f}, ' \
                         f'and we appreciate your support!'
                # Write the letter to a destination
                with open(doc["donor"] + '.txt', 'w') as to_file:
                    to_file.write(letter)
        except Exception as e:
            logger.debug(f'Error writing letters to everyone.')
            logger.debug(e)
        finally:
            logger.debug('Done writing letters.')


class Individual:
    """Connects to MongoDB and works with individual data 'donor' and
     a list of 'donations'.
     """
    def __init__(self, client_path):
        self.db = client_path

    def add_donation(self, person, contribution):

        try:
            logger.debug('Search for donor.')
            result = self.db.find_one({'donor': person})
            if result is None:
                logger.debug('Inserting a new donor')
                self.db.insert_one(
                    {'donor': person,
                     'donations': [contribution]})
            else:
                logger.debug(f'Found {result["donor"]}')
                logger.debug('Adding a new donation to record of donations')
                self.db.find_one_and_update(
                    {'donor': person},
                    {'$push': {'donations': contribution}},
                    return_document=ReturnDocument.AFTER)

        except Exception as e:
            logger.debug(f'Error creating = {person}')
            logger.debug(e)
            logger.debug('Failed to add new donor.')
        finally:
            print('All done adding donor contribution')

    def number_donations(self, name):

        try:
            logger.debug('Trying to count number of donations.')
            result = self.db.find_one({'donor': name})
            if result is None:
                return None
            donations = result['donations']
            return int(len(donations))

        except Exception as e:
            logger.debug(f'Error counting # of donations.')
            logger.debug(e)
        finally:
            logger.debug(f'Returning the # of donations made by {name}')

    def sum_donations(self, name):

        try:
            logger.debug(f'Summing all the donations by {name}.')
            result = self.db.find_one({'donor': name})
            if result is None:
                return None
            sum_donations = sum(result['donations'])
            return sum_donations

        except Exception as e:
            logger.debug(f'Error counting # of donations.')
            logger.debug(e)
        finally:
            logger.debug(f'Returning the # of donations made by {name}')

    def avg_donations(self, name):
        return self.sum_donations(name)/self.number_donations(name)

    def last_donation(self, name):
        try:
            logger.debug(f'Trying to find the last record of {name}.')
            result = self.db.find_one({'donor': name})
            if result is None:
                return None
            logger.debug(f'Finding the last donation made by {name}')
            donation_list = result['donations']
            return donation_list[-1]

        except Exception as e:
            logger.debug(f'Error finding last donation.')
            logger.debug(e)
        finally:
            logger.debug(f'Returning the last donation made by {name}.')

    @staticmethod
    def thank_you(person, contribution):
        """Add a donation to a donors records and print a report."""
        return ('Thank you so much for the generous gift of ${0:.2f}, {1}!'
                .format(contribution, person))

    def delete_donor(self, person):
        try:
            logger.debug(f'Trying to delete {person}.')
            result = self.db.delete_one({'donor': person})
            if result is None:
                return None

        except Exception as e:
            logger.debug(f'Error deleting {person}')
            logger.debug(e)
            logger.debug('Failed to delete donor.')
        finally:

            logger.debug(f'Deletion of {person} successful.')

    @staticmethod
    def donor_verification(path, name):
        """Before entering a new  donor or donation into the database,
         verify that the donor's email, telephone, and address
         of the donor are correct. Add or revise data on record."""

        print(f'Check the information on file for {name}.')
        print(f"{name}'s last name is {path.lindex(name,0)}")
        print(f"{name}'s telephone is {path.lindex(name, 1)}")
        print(f"{name}'s email is {path.lindex(name, 2)}")
        return [path.lindex(name, 0),
                path.lindex(name, 1),
                path.lindex(name, 2)]

    @staticmethod
    def update_last_name(path, name, new_last_name):
        """Update donor's last name in REDIS cache"""
        path.lset(name, 0, new_last_name)
        print(f'Check the information on file for {name}.')
        print(f"{name}'s last name is {path.lindex(name,0)}")
        print(f"{name}'s telephone is {path.lindex(name, 1)}")
        print(f"{name}'s email is {path.lindex(name, 2)}")
        return [path.lindex(name, 0),
                path.lindex(name, 1),
                path.lindex(name, 2)]

    @staticmethod
    def update_telephone(path, name, new_telephone):
        """Update donor's last name in REDIS cache"""
        path.lset(name, 1, new_telephone)
        print(f'Check the information on file for {name}.')
        print(f"{name}'s last name is {path.lindex(name,0)}")
        print(f"{name}'s telephone is {path.lindex(name, 1)}")
        print(f"{name}'s email is {path.lindex(name, 2)}")
        return [path.lindex(name, 0),
                path.lindex(name, 1),
                path.lindex(name, 2)]

    @staticmethod
    def update_email(path, name, new_email):
        """Update donor's last name in REDIS cache"""
        path.lset(name, 2, new_email)
        print(f'Check the information on file for {name}.')
        print(f"{name}'s last name is {path.lindex(name,0)}")
        print(f"{name}'s telephone is {path.lindex(name, 1)}")
        print(f"{name}'s email is {path.lindex(name, 2)}")
        return [path.lindex(name, 0),
                path.lindex(name, 1),
                path.lindex(name, 2)]

    @staticmethod
    def redis_add_new(path, name, last_name, tele, email):
        """Update donor's last name in REDIS cache"""
        path.delete(name)
        path.rpush(name, last_name)
        path.rpush(name, tele)
        path.rpush(name, email)
        print(f'Confirm the information on file for {name}.')
        print(f"{name}'s last name is {path.lindex(name,0)}")
        print(f"{name}'s telephone is {path.lindex(name, 1)}")
        print(f"{name}'s email is {path.lindex(name, 2)}")
        return [path.lindex(name, 0),
                path.lindex(name, 1),
                path.lindex(name, 2)]
