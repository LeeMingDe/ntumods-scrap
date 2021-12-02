import scrapy
from scrapy_splash import SplashRequest


class CourseContentSpider(scrapy.Spider):
    name = 'course_content'
    allowed_domains = ['wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main']
    counter = 0
    prevCourseName = ""
    currentCourseName = ""
    iframe_line = 'iframe = function() { var f = document.getElementsByTagName("iframe")[0].contentDocument; return f.getElementsByTagName("body")[0].innerHTML; }'
    
    def script(self, number):
        return """
            function main(splash, args)
                assert(splash:go(args.url))
                assert(splash:wait(0.25))
                select_xpath = assert(splash:select('select[name="r_course_yr"]'))
                select_xpath:mouse_click()
                {0}
                assert(splash:wait(0.25))
                splash:send_keys("<Enter>")
                assert(splash:wait(0.25))
                load_btn = assert(splash:select('input[type=button]:nth-child(4)'))
                load_btn.mouse_click()
                assert(splash:wait(0.25))

                splash:set_viewport_full()
                
                splash:runjs('iframe = function() {{ var f = document.getElementsByTagName("iframe")[0].contentDocument; return f.getElementsByTagName("body")[0].innerHTML; }}')
                local result = splash:evaljs("iframe()")
                return result
            end
        """.format('splash:send_keys("<Down>")' * number)

    def start_requests(self):
        yield SplashRequest(url="https://wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main", callback=self.parse,
            endpoint="execute", args={'lua_source': self.script(self.counter)}, headers= {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
            }
        )

    def parse(self, response):

        table_counter = 0

        last_table_xpath = response.xpath('//table[last()]/tbody')
        current_table_xpath = response.xpath(f'//table[{table_counter}]/tbody')

        while current_table_xpath.get() != last_table_xpath.get():
            table_row_counter = 2
            table_counter += 1
            current_table_xpath = response.xpath(f'//table[{table_counter}]/tbody')
            module_details = {
                    'course_name': response.xpath('//center/font[1]/b/b/font/text()').get(),
                    'module_code': current_table_xpath.xpath(".//tr[1]/td[1]/b/font/text()").get(),
                    'module_name': current_table_xpath.xpath(".//tr[1]/td[2]/b/font/text()").get(),
                    'module_units': current_table_xpath.xpath("normalize-space(.//tr[1]/td[3]/b/font/text())").get(),
            }

            while response.xpath(f'//table[{table_counter}]/tbody/tr[{table_row_counter}]').get() is not None:
                row_label = current_table_xpath.xpath(f".//tr[{table_row_counter}]/td[1]/b/font/text()").get()
                row_content = current_table_xpath.xpath(f'.//tr[{table_row_counter}]/td[2]/b/font/text()').get()

                if current_table_xpath.xpath(f'.//tr[{table_row_counter}]/td[2]/b/font/text()').get() == current_table_xpath.xpath('.//tr[last()]/td[2]/b/font/text()').get():
                    module_details['module_description'] = current_table_xpath.xpath(f'normalize-space(.//tr[{table_row_counter}]/td/font/text())').get()

                if row_content is None:
                    table_row_counter += 1
                    continue

                if row_label in module_details:
                    module_details[f"{row_label}"]  = module_details[f"{row_label}"] + " " + row_content
                else:
                    module_details[f"{row_label}"]  = row_content
                if row_label == "Prerequisite:":
                    while "OR" in row_content:
                        table_row_counter += 1
                        row_content = current_table_xpath.xpath(f'.//tr[{table_row_counter}]/td[2]/b/font/text()').get()
                        module_details[f"{row_label}"]  = module_details[f"{row_label}"] + " " + row_content
                            
                table_row_counter += 1

            yield module_details

        if self.prevCourseName != "" and self.currentCourseName != "":
            self.prevCourseName = self.currentCourseName
            self.currentCourseName = response.xpath("//center/font[1]/b/b/font/text()").get()

        elif self.prevCourseName != "" and self.currentCourseName == "":
            self.currentCourseName = response.xpath("//center/font[1]/b/b/font/text()").get()

        elif self.prevCourseName == "":
            self.prevCourseName = response.xpath("//center/font[1]/b/b/font/text()").get()

        if self.prevCourseName == self.currentCourseName:
            return

        self.counter += 1

        if self.counter >= 479:
            return

        yield SplashRequest(url="https://wish.wis.ntu.edu.sg/webexe/owa/aus_subj_cont.main", callback=self.parse,
            endpoint="execute", args={'lua_source': self.script(self.counter)}, headers= {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }, dont_filter=True)
