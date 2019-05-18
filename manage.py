import argparse
from importlib import import_module


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--analects_chs', action='store_true')
    parser.add_argument('--analects_cht', action='store_true')
    parser.add_argument('--dictionary', action='store_true')
    parser.add_argument('--fish', action='store_true')
    parser.add_argument('--isitfriday', action='store_true')
    parser.add_argument('--jandan', action='store_true')
    parser.add_argument('--jandan_pic', action='store_true')
    parser.add_argument('--moegirl_daily', action='store_true')
    parser.add_argument('--photo_of_the_day', action='store_true')
    parser.add_argument('--reddit', action='store_true')
    parser.add_argument('--shuowen', action='store_true')
    parser.add_argument('--taoteching', action='store_true')
    parser.add_argument('--word_of_the_day', action='store_true')
    parser.add_argument('--yupian', action='store_true')
    return parser.parse_args()


def main():
    """Main program.

    Parse arguments and run bot.
    """
    args = parse_args()
    for bot_name in vars(args):
        if getattr(args, bot_name) is True:
            module = import_module(f'fanbot.{bot_name}.{bot_name}')
            bot = module.Bot()
            bot.run()


if __name__ == '__main__':
    main()
