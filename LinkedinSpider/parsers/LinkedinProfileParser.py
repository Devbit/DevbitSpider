from LinkedinSpider.items import PersonProfileItem
import re


class LinkedinProfileParser:
    @staticmethod
    def parse_profile(hxs):
        allowed_industries = ["Computer- en netwerkbeveiliging", "Computerhardware", "Computernetwerken", "Computersoftware", "Computerspellen", "Informatieservices", "Informatietechnologie en services", "Internet"]
        person_profile = PersonProfileItem()

        headline = hxs.select("//dl[@id='headline']")
        if headline and len(headline) == 1:
            headline = headline[0]
            ## industry
            industry = headline.select("dd[@class='industry']/text()").extract()
            if industry and len(industry) == 1:
                industry = industry[0].strip()
                if industry in allowed_industries:
                    person_profile['sector'] = industry
                else:
                    return None
            else:
                return None
            ## locality
            locality = headline.select("dd/span[@class='locality']/text()").extract()
            if locality and len(locality) == 1:
                person_profile['location'] = locality[0].strip()

        ## Person name
        name_field = {}
        name_span = hxs.select("//span[@id='name']/span")
        if name_span and len(name_span) == 1:
            name_span = name_span[0]
            given_name_span = name_span.select("span[@class='given-name']")
            if given_name_span and len(given_name_span) == 1:
                given_name_span = given_name_span[0]
                name_field['firstname'] = given_name_span.select("text()").extract()[0]
            family_name_span = name_span.select("span[@class='family-name']")
            if family_name_span and len(family_name_span) == 1:
                family_name_span = family_name_span[0]
                name_field['lastname'] = family_name_span.select("text()").extract()[0]
            person_profile['name'] = name_field
        else:
            return None

        ## profile picture URL
        pic = hxs.select("//div[@id='profile-picture']")
        if pic and len(pic) == 1:
            src = pic.select("img/@src").extract()[0]
            person_profile['picture'] = src

        ## overview
        overview = hxs.select("//dl[@id='overview']").extract()
        if overview and len(overview) == 1:
            person_profile['overview_html'] = " ".join(overview[0].split())

        ## summary
        summary = hxs.select("//div[@id='profile-summary']/div[@class='content']/p[contains(@class,'summary')]/text()").extract()
        if summary and len(summary) > 0:
            person_profile['summary'] = ''.join(x.strip() for x in summary)

        ## specialities
        specialities = hxs.select("//div[@id='profile-specialties']/p/text()").extract()
        if specialities and len(specialities) == 1:
            specialities = specialities[0].strip()
            person_profile['specialities'] = specialities

        ## languages
        langs = hxs.select("//div[@id='profile-languages']//ul/li")
        if langs and len(langs) > 0:
            langlist = []
            for lang in langs:
                l = {}
                name = lang.select('h3/text()').extract()
                if name and len(name) > 0:
                    l['name'] = name[0].strip()
                level = lang.select("span[@class='proficiency']/text()").extract()
                if level and len(level) > 0:
                    l['level'] = level[0].strip()
                langlist.append(l)
            person_profile['languages'] = langlist

        ## skills
        skills = hxs.select("//ol[@id='skills-list']/li/span/text()").extract()
        if skills and len(skills) > 0:
            person_profile['skills'] = [x.strip() for x in skills]

        #additional
        additional = hxs.select("//div[@id='profile-additional']")
        if additional and len(additional) == 1:
            additional = additional[0]
            ## interests
            interests = additional.select("div[@class='content']/dl/dd[@class='interests']/p/text()").extract()
            if interests and len(interests) == 1:
                person_profile['interests'] = interests[0].strip()
            ## groups
            g = additional.select("div[@class='content']/dl/dd[@class='pubgroups']")
            if g and len(g) == 1:
                groups = {}
                g = g[0]
                member = g.select("p/text()").extract()
                if member and len(member) > 0:
                    m = member[0].strip().split(',')
                    m.pop()
                    groups['organisations'] = m
                gs = g.select("ul[@class='groups']/li[contains(@class,'affiliation')]/div/a/strong/text()").extract()
                if gs and len(gs) > 0:
                    groups['groups'] = gs
                person_profile['groups'] = groups
            ## honors
            honors = additional.select("div[@class='content']/dl/dd[@class='honors']/p/text()").extract()
            if honors and len(honors) > 0:
                person_profile['honors'] = [x.strip() for x in honors]

        ## education
        education = hxs.select("//div[@id='profile-education']")
        schools = []
        if education and len(education) == 1:
            education = education[0]
            school_list = education.select("div[contains(@class,'content')]//div[contains(@class,'education')]")
            if school_list and len(school_list) > 0:
                for school in school_list:
                    s = {}
                    name = school.select("h3[contains(@class,'org')]/text()").extract()
                    if name and len(name) == 1:
                        s['school'] = name[0].strip()
                    degree = school.select("h4[@class='details-education']/span[@class='degree']/text()").extract()
                    if degree and len(degree) == 1:
                        s['degree'] = degree[0].strip()
                    major = school.select("h4[@class='details-education']/span[@class='major']/text()").extract()
                    if major and len(major) == 1:
                        s['major'] = major[0].strip()
                    period = school.select("p[@class='period']")
                    if period and len(period) == 1:
                        period = period[0]
                        start = period.select("abbr[@class='dtstart']/text()").extract()
                        end = period.select("abbr[@class='dtend']/text()").extract()
                        if len(start) == 1:
                            s['start'] = start[0]
                        if len(end) == 1:
                            s['end'] = end[0]
                    desc = school.select("p[contains(@class,'desc')]/text()").extract()
                    if len(desc) == 1:
                        s['description'] = desc[0].strip()
                    schools.append(s)
                person_profile['education'] = schools

        ## experience
        experience = hxs.select("//div[@id='profile-experience']")
        if experience and len(experience) == 1:
            es = []
            experience = experience[0]
            exps = experience.select("//div[contains(@class,'experience')]")
            if len(exps) > 0:
                for e in exps:
                    je = {}
                    title = e.select("div[@class='postitle']//span[@class='title']/text()").extract()
                    if len(title) > 0:
                        je['title'] = title[0].strip()
                    org = e.select("div[@class='postitle']//span[contains(@class,'org')]/text()").extract()
                    if len(org) > 0:
                        je['company'] = org[0].strip()
                    # start = e.select("p[@class='period']/abbr[@class='dtstart']/text()").extract()
                    start = e.select("p[@class='period']/abbr[@class='dtstart']/@title").extract()
                    if len(start) > 0:
                        je['start'] = start[0].strip()
                    # end = e.select("p[@class='period']/abbr[@class='dtstamp']/text()").extract()
                    present = e.select("p[@class='period']/abbr[@class='dtstamp']/text()").extract()
                    if len(present) > 0:
                        je['end'] = present[0].strip()
                    else:
                        end = e.select("p[@class='period']/abbr[@class='dtend']/@title").extract()
                        if len(end) > 0:
                            je['end'] = end[0].strip()
                    location = e.select("p[@class='period']/abbr[@class='location']/text()").extract()
                    if len(location) > 0:
                        je['location'] = location[0]
                    desc = e.select("p[contains(@class,'description')]/text()").extract()
                    if len(desc) > 0:
                        je['description'] = "\n".join(x.strip() for x in desc)
                    details = e.select("p[contains(@class, 'organization-details')]/text()").extract()
                    if len(details) > 0:
                        je['details'] = " ".join(details[0].split())
                    es.append(je)
            person_profile['experience'] = es

        ## courses
        course = hxs.select("//div[@id='profile-courses']")
        if course and len(course) == 1:
            courses = []
            course = course[0]
            course_list = course.select("div[contains(@class,'content')]//li[@class='course-group']")
            if course_list and len(course_list) > 0:
                for c in course_list:
                    ce = {}
                    title = []
                    org = c.select("div[@class='postitle']//span[contains(@class,'org')]/text()").extract()
                    if len(org) > 0:
                        ce['organisation'] = org[0].strip()
                        title = c.select("div[@class='postitle']//span[@class='title']/text()").extract()
                    else:
                        title = c.select("h3/text()").extract()
                    if len(title) > 0:
                        ce['title'] = title[0].strip()
                    comp = c.select("ul/li[@class='competency']/text()").extract()
                    if len(comp) > 0:
                        ce['competency'] = [x.strip() for x in comp]
                    courses.append(ce)
            person_profile['courses'] = courses

        return person_profile

    
