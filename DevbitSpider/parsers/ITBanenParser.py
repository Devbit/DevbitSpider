from DevbitSpider.items import VacatureItem
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
        details = {}
        contact = {}
        header = hxs.select("//div[@id='vacature-details']/div[@class='default-huisstijl']/div[contains(@class, 'header')]")
        if header and len(header) == 1:
            header = header[0]
            title = header.select("h1/text()").extract()
            if title and len(title) == 1:
                vacature['title'] = title[0].strip()
            else:
                return None

            subheader = header.select("div[@class='sub-header']")
            if subheader and len(subheader) == 1:
                subheader = subheader[0]
                company = subheader.select("span/a[@class='company-name']/text()").extract()
                if company and len(company) == 1:
                    vacature['company'] = company[0].strip()
                loc = subheader.select("span[@class='company-location']/a/text()").extract()
                if loc and len(loc) == 1:
                    details['location'] = loc[0].strip()

            date = header.select("div[contains(@class, 'vacature-date')]/span/text()").extract()
            if date and len(date) == 1:
                d = date[0].strip()
                if d not in ["vandaag", "gisteren"]:
                    N = re.search("\d+", d).group(0)
                elif d == "vandaag":
                    N = 0
                elif d == "gisteren":
                    N = 1
                date = (datetime.now() - timedelta(days=int(N))).strftime("%d-%m-%Y")
                vacature['date_created'] = date
        else:
            return None

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
                    details['job_type'] = dd[x]
                x = indexsubstr(dt, "Uren")
                if x > -1:
                    details['hours'] = dd[x]
                x = indexsubstr(dt, "Opleidingsniveau")
                if x > -1:
                    details['education_level'] = dd[x]
                x = indexsubstr(dt, "niveau")
                if x > -1:
                    details['career_level'] = dd[x]
                x = indexsubstr(dt, "Salaris")
                if x > -1:
                    details['salary'] = dd[x]

            body = vacature_details.select("//div[contains(@class, 'body')]").extract()
            if body and len(body) == 1:
                details['advert_html'] = " ".join(body[0].split())

        vacature['details'] = details

        contacthtml = hxs.select("//div[@class='contact-info']/div[@class='inner']")
        if contacthtml and len(contacthtml) == 1:
            contacthtml = contacthtml[0]
            addresshtml = contacthtml.select("address/text()").extract()
            address = {}
            if addresshtml and len(addresshtml) == 3:
                addresshtml = [" ".join(x.split()) for x in addresshtml]
                address['company'] = addresshtml[0]
                address['street'] = addresshtml[1]
                splt = addresshtml[2].split(" ")
                address['postal'] = splt[0]
                address['city'] = splt[1]
            gegevens = contacthtml.select('strong[text()="contactgegevens"]')
            if gegevens and len(gegevens) == 1:
                gegevens = gegevens[0]
                gevenstext = gegevens.select("following-sibling::text()").extract()
                brs = gegevens.select("following-sibling::br")
                name = brs[0].select("following-sibling::text()").extract()[0]
                name = " ".join(name.split())
                contact['person'] = name
                telindex = indexsubstr(gevenstext, "Tel")
                if telindex > -1:
                    tel = gevenstext[telindex]
                    tel = tel.split("Tel.: ")[1].strip()
                    contact['phone'] = tel
                faxindex = indexsubstr(gevenstext, "Fax")
                if faxindex > -1:
                    fax = gevenstext[faxindex]
                    fax = fax.split("Fax: ")[1].strip()
                    contact['fax'] = fax
                #mail = contacthtml.select("a[@id='contact-email-link']")
            contact['address'] = address
            vacature['contact'] = contact


        vacid = hxs.select("//var[@id='vacature-id']/text()").extract()
        if vacid and len(vacid) == 1:
            vacature['_id'] = vacid[0]

        logo = hxs.select("//div[@id='detail-page-side']//div[@class='company-logo']/img/@src").extract()
        if logo and len(logo) == 1:
            vacature['logo'] = logo[0]

        return vacature

