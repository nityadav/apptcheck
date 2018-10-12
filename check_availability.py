import argparse
import mechanize
from bs4 import BeautifulSoup
from datetime import datetime
import config


def check_appt(office_code, args):
    form_url = 'https://www.dmv.ca.gov/foa/clear.do?goTo=officeVisit&localeName=en'
    # Fill Browser form
    br = mechanize.Browser()
    br.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')]
    br.open(form_url)
    br.select_form(name="ApptForm")
    br['officeId'] = [office_code]
    br['numberItems'] = [str(args.num_items)]
    if args.license:
        br['taskCID'] = ['true']
    br['firstName'] = args.firstname
    br['lastName'] = args.lastname
    areacode, prefix, suffix = args.phone.split('-')
    br['telArea'] = areacode
    br['telPrefix'] = prefix
    br['telSuffix'] = suffix
    br.submit()
    result_html = br.response().read()
    soup = BeautifulSoup(result_html, 'html.parser')
    results = soup.find_all('td', attrs={'data-title': 'Appointment'})
    if results:
        dt = results[0].find('strong').text.strip()
        appt_date = datetime.strptime(dt, '%A, %B %d, %Y at %I:%M %p')
        return appt_date

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of the script.')
    parser.add_argument('firstname', help='First Name')
    parser.add_argument('lastname', help='Last Name')
    parser.add_argument('phone', help='For example: 555-666-7777')
    parser.add_argument('--license', type=bool, default=True, help='Applying for, replace, or renew a California DL/ID?')
    parser.add_argument('--num_items', type=int, default=1, choices=[1, 2, 3], help='Number of items')
    parser.add_argument('--area', default='south bay', choices=['south bay', 'bay'], help='Area to check for offices')
    args = parser.parse_args()
    for office in config.offices[args.area]:
        available_date = check_appt(office[1], args)
        if available_date:
            print('%s: %s' % (office[0], available_date.ctime()))