import argparse

from fanfou_bot.analects_chs import analects_chs
from fanfou_bot.analects_cht import analects_cht
from fanfou_bot.dictionary import dictionary
from fanfou_bot.fish import fish
from fanfou_bot.isitfriday import isitfriday
from fanfou_bot.jandan import jandan
from fanfou_bot.shuowen import shuowen
from fanfou_bot.yupian import yupian


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--analects_chs', help='analects_chs bot', action='store_true')
    parser.add_argument('--analects_cht', help='analects_cht bot', action='store_true')
    parser.add_argument('--dictionary', help='dictionary bot', action='store_true')
    parser.add_argument('--fish', help='fish bot', action='store_true')
    parser.add_argument('--isitfriday', help='isitfriday bot', action='store_true')
    parser.add_argument('--jandan', help='jandan bot', action='store_true')
    parser.add_argument('--shuowen', help='shuowen bot', action='store_true')
    parser.add_argument('--yupian', help='yupian bot', action='store_true')

    args = parser.parse_args()
    if args.analects_chs:
        bot = analects_chs.AnalectsChsBot()
        bot.run()
    elif args.analects_cht:
        bot = analects_cht.AnalectsChtBot()
        bot.run()
    elif args.dictionary:
        bot = dictionary.DictionaryBot()
        bot.run()
    elif args.fish:
        bot = fish.FishBot()
        # Here is start() for long run
        bot.start()
    elif args.isitfriday:
        bot = isitfriday.IsItFridayBot()
        bot.run()
    elif args.jandan:
        bot = jandan.JandanBot()
        bot.run()
    elif args.shuowen:
        bot = shuowen.ShuowenBot()
        bot.run()
    elif args.yupian:
        bot = yupian.YupianBot()
        bot.run()


if __name__ == '__main__':
    main()
