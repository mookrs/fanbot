import argparse

from fanbot.analects_chs import analects_chs
from fanbot.analects_cht import analects_cht
from fanbot.dictionary import dictionary
from fanbot.fish import fish
from fanbot.isitfriday import isitfriday
from fanbot.jandan import jandan
from fanbot.jandan_pic import jandan_pic
from fanbot.moegirl_daily import moegirl_daily
from fanbot.photo_of_the_day import photo_of_the_day
from fanbot.reddit import reddit
from fanbot.shuowen import shuowen
from fanbot.taoteching import taoteching
from fanbot.word_of_the_day import word_of_the_day
from fanbot.yupian import yupian


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--analects_chs', help='analects_chs bot', action='store_true')
    parser.add_argument('--analects_cht', help='analects_cht bot', action='store_true')
    parser.add_argument('--dictionary', help='dictionary bot', action='store_true')
    parser.add_argument('--fish', help='fish bot', action='store_true')
    parser.add_argument('--isitfriday', help='isitfriday bot', action='store_true')
    parser.add_argument('--jandan', help='jandan bot', action='store_true')
    parser.add_argument('--jandan_pic', help='jandan_pic bot', action='store_true')
    parser.add_argument('--moegirl_daily', help='moegirl_daily bot', action='store_true')
    parser.add_argument('--photo_of_the_day', help='photo_of_the_day bot', action='store_true')
    parser.add_argument('--reddit', help='reddit bot', action='store_true')
    parser.add_argument('--shuowen', help='shuowen bot', action='store_true')
    parser.add_argument('--taoteching', help='taoteching bot', action='store_true')
    parser.add_argument('--word_of_the_day', help='word_of_the_day bot', action='store_true')
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
    elif args.jandan_pic:
        bot = jandan_pic.JandanPicBot()
        bot.run()
    elif args.moegirl_daily:
        bot = moegirl_daily.MoegirlDailyBot()
        bot.run()
    elif args.photo_of_the_day:
        bot = photo_of_the_day.PhotoOfTheDayBot()
        bot.run()
    elif args.reddit:
        bot = reddit.RedditBot()
        bot.run()
    elif args.shuowen:
        bot = shuowen.ShuowenBot()
        bot.run()
    elif args.taoteching:
        bot = taoteching.TaoTeChingBot()
        bot.run()
    elif args.word_of_the_day:
        bot = word_of_the_day.WordOfTheDayBot()
        bot.run()
    elif args.yupian:
        bot = yupian.YupianBot()
        bot.run()


if __name__ == '__main__':
    main()
