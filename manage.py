from fanfou_bot.dictionary import dictionary


def main():
    bot = dictionary.DictionaryBot()
    status = bot.run()

if __name__ == '__main__':
    main()
