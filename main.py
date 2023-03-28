from scrape import VergeScrape
from database import DataBase


if __name__ == "__main__":
    vs = VergeScrape()
    db = DataBase()

    vs.scrape()
    csv_file = vs.convert2csv()
    db.insert_article_from_csv(csv_file)
