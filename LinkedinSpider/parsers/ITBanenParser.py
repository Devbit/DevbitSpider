from LinkedinSpider.items import VacatureItem
from datetime import datetime, timedelta
import re

def indexsubstr(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1

class ITBanenParser:
    @staticmethod
    def parse_profile(hxs):
        vacature = VacatureItem()
        vacature['source'] = "itbanen"
        header = hxs.select("//div[@id='vacature-details']/div[@class='default-huisstijl']/div[contains(@class, 'header')]")
        if header and len(header) == 1:
            header = header[0]
            title = header.select("h1/text()").extract()
            if title and len(title) == 1:
                vacature['title'] = title[0].strip()

            subheader = header.select("div[@class='sub-header']")
            if subheader and len(subheader) == 1:
                subheader = subheader[0]
                company = subheader.select("span/a[@class='company-name']/text()").extract()
                if company and len(company) == 1:
                    vacature['company'] = company[0].strip()
                loc = subheader.select("span[@class='company-location']/a/text()").extract()
                if loc and len(loc) == 1:
                    vacature['location'] = loc[0].strip()

            date = header.select("div[contains(@class, 'vacature-date')]/span/text()").extract()
            if date and len(date) == 1:
                if date[0].strip() not in ["vandaag", "gisteren"]:
                    N = re.search("\d+", date[0].strip()).group(0)
                    date = (datetime.now() - timedelta(days=int(N))).strftime("%d-%m-%Y")
                vacature['date_created'] = date

        vacature_details = hxs.select("//div[@id='vacature-detail-view']")
        if vacature_details and len(vacature_details) == 1:
            vacature_details = vacature_details[0]
            list = vacature_details.select("//dl[@class='hero-list']")
            if list and len(list) == 1:
                list = list[0]
                dt = list.select('dt/text()').extract()
                dd = list.select('dd/text()').extract()
                x = indexsubstr(dt, "verband")
                if x > -1:
                    vacature['job_type'] = dd[x]
                x = indexsubstr(dt, "Uren")
                if x > -1:
                    vacature['hours'] = dd[x]
                x = indexsubstr(dt, "Opleidingsniveau")
                if x > -1:
                    vacature['education_level'] = dd[x]
                x = indexsubstr(dt, "niveau")
                if x > -1:
                    vacature['career_level'] = dd[x]
                x = indexsubstr(dt, "Salaris")
                if x > -1:
                    vacature['salary'] = dd[x]

            body = vacature_details.select("//div[contains(@class, 'body')]").extract()
            if body and len(body) == 1:
                vacature['advert_html'] = " ".join(body[0].split())

        vacid = hxs.select("//var[@id='vacature-id']/text()").extract()
        if vacid and len(vacid) == 1:
            vacature['_id'] = vacid[0]

        return vacature

