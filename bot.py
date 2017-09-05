import configargparse
import requests
import logging
import sys

from time import sleep

logging.basicConfig(level=logging.INFO,
                                format='[%(asctime)s] [%(levelname)5s] %(message)s')

log = logging.getLogger(__name__)

logging.getLogger('requests').setLevel(logging.ERROR)

def main():
    parser = configargparse.ArgumentParser()
    parser.add_argument('-px', '--proxy', help='Proxy to use when version force-checking.')
    parser.add_argument('-wh', '--webhook', help='Discord webhook to push to once a new version is forced.')
    parser.add_argument('-dv', '--default-version', help='Version to default to, skipping initial check.')
    parser.add_argument('-dm', '--discord-message', help='Discord message to send once version forced. '
                                                         'See wiki for details.')
    parser.add_argument('-cd', '--check-delay', default=300, help='Check every X seconds')
    args = parser.parse_args()

    if args.proxy == None:
        log.error('Proxy URL not found, exiting.')
        sys.exit(1)

    version = args.default_version

    if args.default_version == None:
        log.info('Running initial check, to determine version...')
        r = requests.get('https://pgorelease.nianticlabs.com/plfe/version', proxies={
            'http': args.proxy
        })
        version = r.text.replace('\n\x06', '')

    while True:
        log.info('Running version check...')
        r = requests.get('https://pgorelease.nianticlabs.com/plfe/version', proxies={
            'http': args.proxy
        }).text.replace('\n\x06', '')
        if r is not version:
            msg = create_discord_message(version, r, args.discord_message)
            requests.post(args.webhook, data={
                'content': msg
            })
            log.warning('{} is being forced! Sending alert.'.format(r))
        sleep(int(args.check_delay))


def create_discord_message(old_ver, new_ver, template):
    return template.replace('<old>', old_ver).replace('<new>', new_ver)

if __name__ == '__main__':
    main()
